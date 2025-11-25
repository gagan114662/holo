"""
Authentication Router
Handles user registration, login, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
import jwt
import bcrypt
from uuid import UUID

from ..database import get_db
from ..config import settings
from ..models.user import User, UserRole
from ..schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, UserUpdate

router = APIRouter()
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: str, expires_delta: timedelta = None) -> str:
    """Create a JWT access token"""
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    payload = {
        "sub": user_id,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


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
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        result = await db.execute(select(User).where(User.id == UUID(user_id)))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def require_teacher(user: User = Depends(get_current_user)) -> User:
    """Require the user to be a teacher or admin"""
    if user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Teacher access required")
    return user


@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
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
    
    # Generate token
    access_token = create_access_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=86400,  # 24 hours
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with email and password"""
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # Generate token
    access_token = create_access_token(str(user.id))
    
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
async def logout():
    """Logout (client should discard token)"""
    return {"message": "Successfully logged out"}
