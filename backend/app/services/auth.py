import logging
from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.security import (
    create_token,
    hash_password,
    is_token_revoked,
    revoke_token,
    verify_password,
)
from app.models.entities import User
from app.repositories.domain import UserRepository
from app.schemas.dtos import UserCreate

logger = logging.getLogger(__name__)


class AuthService:
    """
    Business logic layer handling user registration, authentication,
    JWT pair generation, token refreshing, and secure token revocation on logout.
    """
    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)
        self.settings = get_settings()

    async def register(self, data: UserCreate) -> User:
        """Register a new user account with hashed password."""
        existing = await self.repo.by_email(data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address is already registered."
            )
        new_user = User(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
        )
        return await self.repo.add(new_user)

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Verify user credentials and issue access + refresh JWT pair."""
        user = await self.repo.by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password provided.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated."
            )
        return {
            "access_token": create_token(str(user.id), self.settings.access_token_minutes, "access"),
            "refresh_token": create_token(str(user.id), self.settings.refresh_token_minutes, "refresh"),
            "token_type": "bearer",
        }

    async def refresh(self, refresh_token_str: str) -> Dict[str, Any]:
        """
        Validate incoming refresh token and issue a fresh access + refresh pair.
        Enforces token type verification and checks revocation status.
        """
        err = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                refresh_token_str,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm]
            )
            token_type = payload.get("type")
            token_jti = payload.get("jti")
            user_id_str = payload.get("sub")

            if token_type != "refresh" or not user_id_str:
                raise err

            if token_jti and await is_token_revoked(token_jti):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh token has been revoked.",
                )

            user_id = int(user_id_str)
        except (JWTError, ValueError):
            raise err

        user = await self.repo.get(user_id)
        if not user or not user.is_active:
            raise err

        # Optionally revoke the old refresh token upon rotation
        if token_jti:
            await revoke_token(token_jti, self.settings.refresh_token_minutes * 60)

        return {
            "access_token": create_token(str(user.id), self.settings.access_token_minutes, "access"),
            "refresh_token": create_token(str(user.id), self.settings.refresh_token_minutes, "refresh"),
            "token_type": "bearer",
        }

    async def logout(self, access_token_str: str) -> Dict[str, str]:
        """
        Revoke the provided access token by storing its JTI in the blacklist.
        """
        try:
            # Decode options to allow extracting JTI even if slightly near expiration during logout
            payload = jwt.decode(
                access_token_str,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
                options={"verify_exp": False}
            )
            token_jti = payload.get("jti")
            exp_timestamp = payload.get("exp")
            if token_jti:
                ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp()) if exp_timestamp else 3600
                await revoke_token(token_jti, max(10, ttl))
        except Exception as exc:
            logger.warning("Error decoding token during logout revocation: %s", exc)

        return {"detail": "Successfully logged out and token revoked."}
