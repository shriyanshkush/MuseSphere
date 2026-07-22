import logging
from typing import Any, Dict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.api.routes import routers
from app.core.config import get_settings
from app.core.limiter import limiter
import app.models  # noqa: F401 - Ensure models are loaded in registry for Alembic

# Configure application logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()

OPENAPI_TAGS = [
    {
        "name": "Authentication & Profile",
        "description": "User account registration, JWT token login, token refresh, and profile management.",
    },
    {
        "name": "Exhibitions Catalog",
        "description": "Explore and manage museum exhibitions, gallery locations, timings, and popularity scores.",
    },
    {
        "name": "Live Events & Workshops",
        "description": "Discover scheduled museum events, guided tours, lectures, and workshops.",
    },
    {
        "name": "Ticket Bookings",
        "description": "Reserve entry tickets with automated slot capacity checking and dynamic pricing.",
    },
    {
        "name": "Payments Gateway Integration",
        "description": "Initiate Razorpay checkout orders and verify cryptographic transaction signatures.",
    },
    {
        "name": "QR Tickets",
        "description": "Retrieve digital entry passes formatted as base64 PNG QR images.",
    },
    {
        "name": "AI Chatbot & RAG Assistant",
        "description": "Multilingual conversational AI powered by Google Gemini and ChromaDB vector search.",
    },
    {
        "name": "RAG Knowledge Base Administration",
        "description": "Upload, chunk, and index museum guides and documents into vector storage.",
    },
    {
        "name": "ML Recommendation Engine",
        "description": "Personalized exhibition suggestions using machine learning preference matching.",
    },
    {
        "name": "Visitor Feedback & Sentiment Analysis",
        "description": "Submit reviews and automatically classify sentiment into positive, neutral, or negative.",
    },
    {
        "name": "Admin Analytics Dashboard",
        "description": "Telemetric KPI summary covering visitor traffic, revenue, and language distribution.",
    },
    {
        "name": "System",
        "description": "Health check and diagnostic probes.",
    },
]

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description=(
        "**MuseSphere API** is an enterprise, production-ready backend powering a next-generation museum experience. "
        "Built with standard layered Clean Architecture, asynchronous SQLAlchemy 2.0 (`AsyncSession`), Pydantic v2 validation, "
        "Alembic schema migrations, SlowAPI rate limiting, Redis token revocation, and Google Gemini + ChromaDB RAG workflows.\n\n"
        "### Key Capabilities\n"
        "* **Role-Based Access Control**: JWT bearer tokens with refresh rotation and logout revocation (`/auth`).\n"
        "* **Dynamic Ticketing & Capacity**: Real-time slot booking verification (`/bookings`).\n"
        "* **Secure Gateway Checkout**: Razorpay mock integration with digital QR pass generation (`/payments`, `/tickets`).\n"
        "* **Conversational RAG AI**: Multilingual assistance (`en`, `hi`, `fr`, `es`, `de`) over vector embeddings (`/chat/message`).\n"
        "* **Machine Learning & Sentiment**: Personalized exhibit recommendations (`/recommendations`) and review classification (`/feedback/analyze`)."
    ),
    openapi_tags=OPENAPI_TAGS,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Connect SlowAPI rate limiter middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
for router in routers:
    app.include_router(router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    """Global fallback exception handler for unhandled errors."""
    logger.exception("Unhandled application error encountered: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal server error occurred. Please contact support."},
    )


@app.get("/health", tags=["System"], summary="Application health check probe")
async def health() -> Dict[str, Any]:
    """
    Returns system status, service name, active environment, and LLM provider mode.
    Used by load balancers, Docker healthchecks, and AWS container monitors.
    """
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.environment,
        "llm_provider": settings.llm_provider,
        "database": "postgresql_or_sqlite_async",
    }
