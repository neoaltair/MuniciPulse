"""
JWT Authentication and authorization utilities with OAuth2 scopes
"""
from datetime import datetime, timedelta
from typing import Optional, List
from jose import JWTError, jwt
import bcrypt  # Direct bcrypt usage instead of passlib
from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

from database import get_db
from models import User, UserRole
from schemas import TokenData

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2 scheme with scopes
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/login",
    scopes={
        "citizen": "Access to citizen endpoints (create reports, view own reports)",
        "officer": "Access to officer endpoints (update status, view all reports)"
    }
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt"""
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def get_scopes_for_role(role: UserRole) -> List[str]:
    """
    Get OAuth2 scopes based on user role
    
    Args:
        role: User role
    
    Returns:
        List of scopes for the role
    """
    if role == UserRole.CITIZEN:
        return ["citizen"]
    elif role == UserRole.MUNICIPAL_OFFICER:
        return ["officer"]
    return []


def create_access_token(user: User, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with OAuth2 scopes
    
    Args:
        user: User object
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token with scopes
    """
    # Get scopes based on user role
    scopes = get_scopes_for_role(user.role)
    
    # Create token data
    to_encode = {
        "sub": str(user.id),
        "role": user.role.value,
        "scopes": scopes
    }
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password
    
    Args:
        db: Database session
        username: User's username
        password: User's plain password
    
    Returns:
        User object if authenticated, None otherwise
    """
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user



async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token and validate OAuth2 scopes
    
    Args:
        security_scopes: Required OAuth2 scopes for the endpoint
        token: JWT token from request
        db: Database session
    
    Returns:
        Current user object
    
    Raises:
        HTTPException: If token is invalid, user not found, or scopes insufficient
    """
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_scopes: List[str] = payload.get("scopes", [])
        
        if user_id is None:
            raise credentials_exception
        
        token_data = TokenData(user_id=user_id, scopes=token_scopes)
    except JWTError:
        raise credentials_exception
    
    # Validate that token has all required scopes
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required scope: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_citizen(
    current_user: User = Security(get_current_user, scopes=["citizen"])
) -> User:
    """
    Ensure the current user has 'citizen' OAuth2 scope
    
    Args:
        current_user: Current authenticated user (validated with 'citizen' scope)
    
    Returns:
        Current user if they have citizen scope
    """
    return current_user


async def get_current_municipal_officer(
    current_user: User = Security(get_current_user, scopes=["officer"])
) -> User:
    """
    Ensure the current user has 'officer' OAuth2 scope
    
    Args:
        current_user: Current authenticated user (validated with 'officer' scope)
    
    Returns:
        Current user if they have officer scope
    """
    return current_user
