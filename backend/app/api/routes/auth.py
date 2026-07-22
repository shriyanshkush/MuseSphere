from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user, oauth2_scheme
from app.database.session import get_db
from app.models.entities import User
from app.schemas.dtos import LoginRequest, TokenPair, UserCreate, UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication & Profile"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new visitor or admin account",
    description="Validates input credentials and creates a secure user profile with bcrypt password hashing.",
    response_description="Newly created user profile metadata (excluding sensitive password hash).",
    responses={
        409: {"description": "Email address is already registered in the system."},
        422: {"description": "Validation error on input fields (e.g. invalid email format or weak password)."}
    }
)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    """Register a new user account."""
    return await AuthService(db).register(data)


@router.post(
    "/login",
    response_model=TokenPair,
    summary="Authenticate user and issue JWT token pair",
    description="Verifies visitor email and password, returning a short-lived access token and long-lived refresh token.",
    response_description="Access and refresh JWT pair with bearer token scheme.",
    responses={
        401: {"description": "Invalid email or password."},
        403: {"description": "User account has been deactivated."}
    }
)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)) -> dict:
    """Login and obtain access/refresh token pair."""
    return await AuthService(db).login(data.email, data.password)


@router.post(
    "/refresh",
    response_model=TokenPair,
    summary="Rotate tokens using a valid refresh token",
    description="Validates the provided refresh token and issues a new access and refresh JWT pair. Rejects standard access tokens or blacklisted tokens.",
    response_description="Fresh access and refresh JWT token pair.",
    responses={
        401: {"description": "Refresh token expired, invalid, or revoked."}
    }
)
async def refresh(
    refresh_token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Obtain a new token pair using a valid refresh token."""
    return await AuthService(db).refresh(refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="Logout user and revoke access token",
    description="Adds the current JWT token JTI to the Redis/in-memory blacklist, preventing further access across all endpoints.",
    response_description="Confirmation message that the token has been revoked.",
    responses={
        401: {"description": "Missing or invalid authorization token."}
    }
)
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Revoke active JWT token upon user logout."""
    return await AuthService(db).logout(token)


@router.get(
    "/profile",
    response_model=UserRead,
    summary="Retrieve authenticated user profile",
    description="Returns full profile information, role status, and preferred language for the currently authenticated visitor.",
    response_description="User profile summary object.",
    responses={
        401: {"description": "Unauthorized access attempt."}
    }
)
async def profile(user: User = Depends(get_current_user)) -> User:
    """Get current authenticated user profile."""
    return user
