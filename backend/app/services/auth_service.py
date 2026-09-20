"""
FeeAssist AI — Authentication Service

Business logic for registration and login.
Keeps the API router thin and testable.
"""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest
from app.security.auth import hash_password, verify_password, create_access_token


def register_user(data: RegisterRequest, db: Session) -> User:
    """
    Register a new user.

    Raises:
        400 if email already exists.
    """
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
        preferred_language=data.preferred_language,
        course=data.course,
        year=data.year,
        semester=data.semester,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def login_user(data: LoginRequest, db: Session) -> str:
    """
    Authenticate a user and return a JWT access token.

    Raises:
        401 with a generic message — does NOT reveal whether
        the email or password was the specific cause.
    """
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = db.query(User).filter(User.email == data.email).first()
    if user is None:
        raise auth_error

    if not verify_password(data.password, user.password_hash):
        raise auth_error

    return create_access_token(subject=user.id)
