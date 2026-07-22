import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional, Set
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis
from app.core.config import get_settings
from app.database.session import get_db
from app.models.entities import User, UserRole

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# In-memory fallback blacklist set when Redis is unreachable locally
_IN_MEMORY_BLACKLIST: Set[str] = set()
_redis_pool: Optional[aioredis.Redis] = None


async def get_redis_client() -> Optional[aioredis.Redis]:
    """Get or initialize asynchronous Redis connection pool."""
    global _redis_pool
    settings = get_settings()
    if _redis_pool is None and settings.redis_url:
        try:
            _redis_pool = aioredis.from_url(settings.redis_url, decode_responses=True)
            await _redis_pool.ping()
        except Exception as exc:
            logger.warning("Could not connect to Redis (%s). Using in-memory token blacklist.", exc)
            _redis_pool = None
    return _redis_pool


async def is_token_revoked(token_jti: str) -> bool:
    """Check whether a JWT token JTI has been revoked/blacklisted."""
    if not token_jti:
        return False
    redis_client = await get_redis_client()
    if redis_client is not None:
        try:
            val = await redis_client.get(f"blacklist:{token_jti}")
            return val is not None
        except Exception:
            pass
    return token_jti in _IN_MEMORY_BLACKLIST


async def revoke_token(token_jti: str, ttl_seconds: int = 86400) -> None:
    """Add a JWT JTI to the revocation blacklist with expiration TTL."""
    if not token_jti:
        return
    redis_client = await get_redis_client()
    if redis_client is not None:
        try:
            await redis_client.setex(f"blacklist:{token_jti}", max(10, ttl_seconds), "revoked")
            return
        except Exception:
            pass
    _IN_MEMORY_BLACKLIST.add(token_jti)


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against stored bcrypt hash."""
    return pwd_context.verify(password, hashed_password)


def create_token(subject: str, minutes: int, token_type: str = "access") -> str:
    """
    Encode and sign a secure JSON Web Token with a unique JTI identifier.
    """
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=minutes)
    payload = {
        "sub": subject,
        "type": token_type,
        "jti": str(uuid.uuid4()),
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency: Verifies incoming JWT access token, checks revocation status,
    and fetches the authenticated user entity from database.
    """
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id_str: Optional[str] = payload.get("sub")
        token_jti: Optional[str] = payload.get("jti")
        token_type: Optional[str] = payload.get("type")

        if user_id_str is None or token_type != "access":
            raise credentials_exception

        if token_jti and await is_token_revoked(token_jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked upon logout",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise credentials_exception
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    """
    FastAPI dependency: Enforces Role-Based Access Control requiring Admin privileges.
    """
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required for this operation",
        )
    return user
