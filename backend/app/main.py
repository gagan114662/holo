"""
HoloTutor FastAPI Application
Main entry point for the AI tutoring backend
"""
import time
import logging
from typing import Callable
from collections import defaultdict

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base, get_db
from .routers import auth, questions, sessions, progress, teachers, avatars, avatar_generation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Rate limiting storage (in production, use Redis)
rate_limit_storage: dict[str, list[float]] = defaultdict(list)


class RateLimiter:
    """Simple in-memory rate limiter (use Redis in production for distributed systems)"""

    def __init__(self, requests: int, window_seconds: int):
        self.requests = requests
        self.window_seconds = window_seconds

    def is_allowed(self, client_id: str) -> bool:
        """Check if a request is allowed for this client"""
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old requests
        rate_limit_storage[client_id] = [
            ts for ts in rate_limit_storage[client_id] if ts > window_start
        ]

        # Check if under limit
        if len(rate_limit_storage[client_id]) >= self.requests:
            return False

        # Record this request
        rate_limit_storage[client_id].append(now)
        return True

    def get_retry_after(self, client_id: str) -> int:
        """Get seconds until next request is allowed"""
        if not rate_limit_storage[client_id]:
            return 0
        oldest = min(rate_limit_storage[client_id])
        return max(0, int(oldest + self.window_seconds - time.time()))


rate_limiter = RateLimiter(
    requests=settings.rate_limit_requests,
    window_seconds=settings.rate_limit_window_seconds
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    logger.info("Starting HoloTutor API...")

    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database tables initialized")
    yield

    # Shutdown: Close connections
    logger.info("Shutting down HoloTutor API...")
    await engine.dispose()


app = FastAPI(
    title="HoloTutor API",
    description="AI Tutoring Platform Backend - Learn from History's Greatest Minds",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware with explicit methods/headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With"],
)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next: Callable) -> Response:
    """Rate limiting middleware"""
    # Skip rate limiting for health check
    if request.url.path in ["/health", "/", "/docs", "/openapi.json"]:
        return await call_next(request)

    # Get client identifier (IP or user ID from token)
    client_id = request.client.host if request.client else "unknown"

    # Check rate limit
    if not rate_limiter.is_allowed(client_id):
        retry_after = rate_limiter.get_retry_after(client_id)
        logger.warning(f"Rate limit exceeded for {client_id}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests. Please try again later."},
            headers={"Retry-After": str(retry_after)}
        )

    return await call_next(request)


@app.middleware("http")
async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """Request logging middleware"""
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s"
    )

    return response

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Tutoring Sessions"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress Tracking"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teacher Dashboard"])
app.include_router(avatars.router, prefix="/api/avatars", tags=["Avatar System"])
app.include_router(avatar_generation.router, prefix="/api/avatars/generated", tags=["Avatar Generation"])


@app.get("/")
async def root():
    return {
        "message": "HoloTutor API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint that verifies database connectivity"""
    health_status = {
        "status": "healthy",
        "database": "unknown",
        "version": "1.0.0"
    }

    # Check database connectivity
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database"] = f"error: {str(e)}"
        logger.error(f"Health check database error: {e}")

    return health_status
