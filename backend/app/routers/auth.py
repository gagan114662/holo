"""
Authentication Router
Handles user registration, login, and token management
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from jose import jwt, JWTError
import bcrypt
from uuid import UUID
import secrets
from collections import defaultdict
import time

from ..database import get_db
from ..config import settings
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# Token blacklist storage (use Redis in production for distributed systems)
# Stores {jti: expiry_timestamp} to auto-clean expired tokens
_token_blacklist: dict[str, float] = {}
_blacklist_cleanup_threshold = 1000  # Clean up when this many tokens are blacklisted


def _cleanup_expired_blacklist():
    """Remove expired tokens from blacklist"""
    global _token_blacklist
    now = time.time()
    _token_blacklist = {jti: exp for jti, exp in _token_blacklist.items() if exp > now}


def is_token_blacklisted(jti: str) -> bool:
    """Check if a token is blacklisted"""
    if len(_token_blacklist) > _blacklist_cleanup_threshold:
        _cleanup_expired_blacklist()
    return jti in _token_blacklist and _token_blacklist[jti] > time.time()


def blacklist_token(jti: str, exp: float):
    """Add a token to the blacklist"""
    _token_blacklist[jti] = exp


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: str, expires_delta: timedelta = None) -> tuple[str, str]:
    """Create a JWT access token. Returns (token, jti)"""
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    jti = secrets.token_urlsafe(16)  # Unique token ID for blacklisting
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": jti
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
    return token, jti


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user from JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        jti = payload.get("jti")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Check if token is blacklisted
        if jti and is_token_blacklisted(jti):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except JWTError as e:
        if "expired" in str(e).lower():
            raise HTTPException(status_code=401, detail="Token expired")
        raise HTTPException(status_code=401, detail="Invalid token")


async def require_teacher(user: User = Depends(get_current_user)) -> User:
    """Require the user to be a teacher or admin"""
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Teacher access required")
    return user


async def verify_websocket_token(token: str, db: AsyncSession) -> User | None:
    """Verify a JWT token for WebSocket connections (returns None instead of raising)"""
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            return None

        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        return result.scalar_one_or_none()
    except JWTError:
        return None


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    logger.info(f"Registration attempt for email: {user_data.email}")

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        logger.warning(f"Registration failed - email already exists: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        display_name=user_data.display_name,
        role=user_data.role,
        grade_level=user_data.grade_level,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f"User registered successfully: {user.id} ({user.email})")

    # Generate token
    access_token, _ = create_access_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,  # 24 hours
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with email and password"""
    logger.info(f"Login attempt for email: {credentials.email}")

    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Failed login attempt for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()

    logger.info(f"User logged in successfully: {user.id} ({user.email})")

    # Generate token
    access_token, _ = create_access_token(str(user.id))

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    updates: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    if updates.display_name:
        user.display_name = updates.display_name
    if updates.grade_level:
        user.grade_level = updates.grade_level
    if updates.avatar_url:
        user.avatar_url = updates.avatar_url
    
    await db.commit()
    await db.refresh(user)
    
    return UserResponse.model_validate(user)


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Logout and invalidate the current token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=["HS256"]
        )
        jti = payload.get("jti")
        exp = payload.get("exp", 0)

        if jti:
            # Add token to blacklist until it expires
            blacklist_token(jti, exp)
            logger.info(f"Token blacklisted: {jti[:8]}...")

        return {"message": "Successfully logged out"}
    except JWTError:
        # Token is invalid anyway, just return success
        return {"message": "Successfully logged out"}
