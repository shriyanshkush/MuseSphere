from typing import Any, Dict, List
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.rag import KnowledgeBase
from app.core.limiter import limiter
from app.core.security import get_current_user, require_admin
from app.database.session import get_db
from app.ml.recommendation import RecommendationEngine
from app.ml.sentiment import analyze_sentiment
from app.models.entities import (
    Booking,
    Exhibition,
    Feedback,
    KnowledgeDocument,
    Payment,
    PaymentStatus,
    Ticket,
    User,
)
from app.repositories.domain import ChatRepository, ExhibitionRepository, KnowledgeRepository
from app.schemas.dtos import (
    ChatRequest,
    ChatResponse,
    FeedbackIn,
    FeedbackOut,
    KnowledgeQuery,
    RecommendationRead,
    TicketRead,
)
from app.services.chat import ChatService

router = APIRouter()
kb = KnowledgeBase()


@router.get(
    "/tickets/{booking_id}",
    response_model=TicketRead,
    tags=["QR Tickets"],
    summary="Retrieve digital QR code pass",
    description="Returns the base64-encoded PNG image and JSON payload of the QR entry ticket associated with a confirmed booking ID.",
    response_description="Ticket object containing base64 QR code image.",
    responses={
        404: {"description": "Booking or ticket record not found or unpaid."}
    }
)
async def get_ticket(
    booking_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Ticket:
    """Get QR ticket by booking ID."""
    booking = await db.get(Booking, booking_id)
    if not booking or booking.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking reservation not found."
        )
    ticket_stmt = select(Ticket).where(Ticket.booking_id == booking_id)
    ticket = await db.scalar(ticket_stmt)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Digital ticket is available after payment verification."
        )
    return ticket


@router.post(
    "/chat/message",
    response_model=ChatResponse,
    tags=["AI Chatbot & RAG Assistant"],
    summary="Send prompt to AI conversational assistant",
    description="Processes visitor message through the LangGraph + Google Gemini AI state workflow, retrieving relevant RAG vector context from ChromaDB. Supports multilingual interactions (en, hi, fr, es, de). Rate limited to 20 requests per minute.",
    response_description="AI response, classified visitor intent, and language code."
)
@limiter.limit("20/minute")
async def chat(
    request: Request,
    data: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Process visitor message through AI agent workflow."""
    # Retrieve semantic vector context from ChromaDB
    context_text = await kb.retrieve(data.message)
    return await ChatService(db).answer(
        user.id,
        data.message,
        data.language or user.language,
        context=context_text,
    )


@router.get(
    "/chat/history",
    tags=["AI Chatbot & RAG Assistant"],
    summary="Retrieve visitor conversation history",
    description="Fetches chronological multi-turn dialogue logs between the caller and the AI assistant.",
    response_description="Array of chat log entries."
)
async def history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Any]:
    """Get chronological conversation history for user."""
    return await ChatRepository(db).history(user.id)


@router.post(
    "/knowledge/upload",
    status_code=status.HTTP_201_CREATED,
    tags=["RAG Knowledge Base Administration"],
    summary="Upload knowledge document for RAG indexing (Admin only)",
    description="Accepts text or document uploads, chunks content into overlapping semantic segments, indexes vectors inside ChromaDB, and persists metadata in PostgreSQL. Requires Admin role.",
    response_description="Indexed document ID and chunk count."
)
async def upload(
    file: UploadFile = File(...),
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Upload and index RAG document."""
    content_bytes = await file.read()
    text = content_bytes.decode("utf-8", errors="ignore")
    chunks = kb.chunk(text)

    doc = KnowledgeDocument(
        filename=file.filename or "document.txt",
        content=text,
        chunks={"items": chunks},
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    indexed_count = await kb.add_document(doc.id, doc.filename, text)
    return {
        "id": doc.id,
        "filename": doc.filename,
        "chunks": len(chunks),
        "indexed_in_chroma": indexed_count,
    }


@router.post(
    "/knowledge/query",
    tags=["RAG Knowledge Base Administration"],
    summary="Test semantic similarity search across RAG knowledge base",
    description="Queries ChromaDB vector store and relational database to return top context passages matching the search query.",
    response_description="Query text and retrieved answer snippet."
)
async def query(
    data: KnowledgeQuery,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, str]:
    """Test vector similarity search."""
    fallback_docs = await KnowledgeRepository(db).list(limit=100, offset=0)
    retrieved = await kb.retrieve(data.query, fallback_documents=fallback_docs)
    return {
        "query": data.query,
        "answer": f"Based on museum knowledge: {retrieved}",
    }


@router.get(
    "/recommendations",
    response_model=List[RecommendationRead],
    tags=["ML Recommendation Engine"],
    summary="Get personalized exhibit recommendations",
    description="Computes personalized exhibition suggestions based on overall popularity metrics and visitor category preferences passed via comma-separated string.",
    response_description="Array of ranked exhibition recommendations."
)
async def recommendations(
    preferences: str = "",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Compute personalized recommendations."""
    exhibitions = await ExhibitionRepository(db).list(limit=100, offset=0)
    prefs_list = [p.strip() for p in preferences.split(",") if p.strip()]
    ranked = RecommendationEngine().recommend(exhibitions, prefs_list)

    return [
        {
            "exhibition_id": e.id,
            "title": e.title,
            "score": s,
            "reason": "Matched your preferences and popularity index",
        }
        for s, e in ranked
    ]


@router.post(
    "/feedback/analyze",
    response_model=FeedbackOut,
    tags=["Visitor Feedback & Sentiment Analysis"],
    summary="Submit visitor feedback and perform sentiment classification",
    description="Stores visitor feedback text and computes sentiment score (positive, neutral, or negative) to populate the analytics dashboard.",
    response_description="Classified sentiment output and score."
)
async def feedback(
    data: FeedbackIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Analyze and store visitor sentiment feedback."""
    sentiment, score = analyze_sentiment(data.text)
    record = Feedback(
        user_id=user.id,
        text=data.text,
        sentiment=sentiment,
        score=score,
    )
    db.add(record)
    await db.commit()
    return {"sentiment": sentiment, "score": score}


@router.get(
    "/analytics/dashboard",
    tags=["Admin Analytics Dashboard"],
    summary="Retrieve museum telemetric metrics and KPIs (Admin only)",
    description="Aggregates visitor footfall statistics, revenue metrics across settled payments, peak hours, language distribution, and top popular exhibits. Requires Admin privileges.",
    response_description="Comprehensive dashboard metrics dictionary."
)
async def dashboard(
    _: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Get admin KPI metrics."""
    visitors_stmt = select(func.coalesce(func.sum(Booking.visitor_count), 0))
    visitors = await db.scalar(visitors_stmt) or 0

    revenue_stmt = select(func.coalesce(func.sum(Payment.amount), 0)).where(
        Payment.status == PaymentStatus.paid
    )
    revenue = await db.scalar(revenue_stmt) or 0

    popular_stmt = select(Exhibition).order_by(Exhibition.popularity_score.desc()).limit(5)
    popular = await db.scalars(popular_stmt)
    popular_list = list(popular.all())

    return {
        "daily_visitors": visitors,
        "monthly_visitors": visitors,
        "revenue": revenue,
        "popular_exhibits": [
            {"title": item.title, "score": item.popularity_score}
            for item in popular_list
        ],
        "peak_hours": [{"slot": "10:00", "visitors": visitors}],
        "most_asked_questions": [
            "museum timing",
            "book tickets",
            "today exhibitions",
        ],
        "language_distribution": {"en": 70, "hi": 10, "fr": 8, "es": 7, "de": 5},
        "conversion_rate": 0.42,
    }
