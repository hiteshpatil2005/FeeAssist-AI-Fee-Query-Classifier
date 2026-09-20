"""
FeeAssist AI — Authentication API Router

Endpoints:
  POST /api/auth/register  — Create a new user account
  POST /api/auth/login     — Authenticate and receive JWT
  GET  /api/auth/me        — Return the current authenticated user
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserOut
from app.security.auth import get_current_user
from app.services.auth_service import register_user, login_user

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new student account",
)
def register(
    data: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Create a new user account.
    Password is hashed before storage — plain text is never saved.
    """
    user = register_user(data, db)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive a JWT access token",
)
def login(
    data: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
):
    """
    Authenticate with email and password.
    Returns a Bearer JWT token on success.
    Returns 401 on invalid credentials — does not reveal which field was wrong.
    """
    token = login_user(data, db)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get the currently authenticated user",
)
def me(
    current_user: Annotated[User, Depends(get_current_user)],
):
    """
    Returns the profile of the currently authenticated user.
    Password hash is never included in the response.
    """
    return current_user
