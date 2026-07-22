from functools import lru_cache
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application core settings loaded from environment variables or .env file.
    Follows strict Pydantic v2 validation and PEP 8 multi-line formatting.
    """
    # Application & Environment
    app_name: str = Field(default="MuseSphere API", description="Application display name")
    environment: str = Field(default="development", description="Environment: development, staging, or production")
    cors_origins: List[str] = Field(
        default=["*"],
        description="Allowed CORS origins for API requests"
    )

    # Database & ORM Connection Pooling
    database_url: str = Field(
        default="sqlite+aiosqlite:///./museai.db",
        description="Asynchronous connection string for PostgreSQL or SQLite"
    )
    db_pool_size: int = Field(default=10, description="Database connection pool size")
    db_max_overflow: int = Field(default=20, description="Maximum number of connections beyond pool_size")
    db_pool_timeout: int = Field(default=30, description="Timeout in seconds before raising connection error")
    db_pool_recycle: int = Field(default=1800, description="Recycle connections older than this in seconds")
    db_echo: bool = Field(default=False, description="Enable SQLAlchemy SQL query logging")

    # Redis & Rate Limiting
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URI")
    rate_limit_enabled: bool = Field(default=True, description="Enable API rate limiting")

    # JWT Authentication & Security
    jwt_secret: str = Field(
        default="change-me-in-production-secret-key-32chars",
        min_length=16,
        description="Secret key for JWT signature encoding/decoding"
    )
    jwt_algorithm: str = Field(default="HS256", description="JWT signing algorithm")
    access_token_minutes: int = Field(default=60, description="Access token lifespan in minutes")
    refresh_token_minutes: int = Field(default=10080, description="Refresh token lifespan in minutes (7 days)")

    # Razorpay Payment Gateway Demo Credentials
    razorpay_key_id: str = Field(default="rzp_test_mock_key", description="Razorpay API Key ID")
    razorpay_key_secret: str = Field(default="rzp_test_mock_secret", description="Razorpay API Key Secret")

    # AI, RAG & Vector Store Integration
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API Key for LangGraph AI Assistant"
    )
    llm_provider: str = Field(default="gemini", description="LLM provider: gemini or mock")
    chroma_host: str = Field(default="localhost", description="ChromaDB server hostname")
    chroma_port: int = Field(default=8001, description="ChromaDB server port")
    chroma_collection: str = Field(default="muse_knowledge", description="ChromaDB vector collection name")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings singleton factory.
    """
    return Settings()
