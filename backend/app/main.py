"""
HoloTutor FastAPI Application
Main entry point for the AI tutoring backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .config import settings
from .database import engine, Base
from .routers import auth, questions, sessions, progress, teachers, avatars

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager"""
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Shutdown: Close connections
    await engine.dispose()


app = FastAPI(
    title="HoloTutor API",
    description="AI Tutoring Platform Backend - Learn from History's Greatest Minds",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(questions.router, prefix="/api/questions", tags=["Questions"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Tutoring Sessions"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress Tracking"])
app.include_router(teachers.router, prefix="/api/teachers", tags=["Teacher Dashboard"])
app.include_router(avatars.router, prefix="/api/avatars", tags=["Avatar System"])


@app.get("/")
async def root():
    return {
        "message": "HoloTutor API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
