import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base


class UserRole(str, enum.Enum):
    """Roles available in the system."""
    visitor = "visitor"
    admin = "admin"


class PaymentStatus(str, enum.Enum):
    """Lifecycle status of a payment transaction."""
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class BookingStatus(str, enum.Enum):
    """Lifecycle status of a museum ticket booking."""
    pending_payment = "pending_payment"
    confirmed = "confirmed"
    cancelled = "cancelled"


class User(Base):
    """
    Represents a registered museum visitor or administrative user.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.visitor, nullable=False)
    language: Mapped[str] = mapped_column(String(12), default="en", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Exhibition(Base):
    """
    Represents a curated exhibition inside the museum.
    """
    __tablename__ = "exhibitions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(120), nullable=False)
    image: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timings: Mapped[str] = mapped_column(String(120), default="10:00-18:00", nullable=False)
    popularity_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class Event(Base):
    """
    Represents a scheduled live event, workshop, or guided tour.
    """
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=50, nullable=False)
    price: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)


class Booking(Base):
    """
    Represents a ticket reservation made by a user for a specific visit slot.
    """
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    visit_date: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    time_slot: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    ticket_type: Mapped[str] = mapped_column(String(60), nullable=False)
    visitor_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        default=BookingStatus.pending_payment,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship()


class Payment(Base):
    """
    Tracks payment gateway order records and verification statuses linked to a booking.
    """
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), nullable=False)
    transaction_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    provider_order_id: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(PaymentStatus),
        default=PaymentStatus.pending,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Ticket(Base):
    """
    Represents an issued QR code digital pass for a confirmed booking.
    """
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), unique=True, nullable=False)
    qr_payload: Mapped[str] = mapped_column(Text, nullable=False)
    qr_code_base64: Mapped[str] = mapped_column(Text, nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class ChatHistory(Base):
    """
    Logs multi-turn conversational messages between visitors and the AI assistant.
    """
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    response: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(12), default="en", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class KnowledgeDocument(Base):
    """
    Stores uploaded museum guides, brochures, and historical documents chunked for RAG.
    """
    __tablename__ = "knowledge_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunks: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Feedback(Base):
    """
    Stores visitor feedback submissions and computed sentiment classification scores.
    """
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class Recommendation(Base):
    """
    Stores precomputed machine learning recommendations for a visitor.
    """
    __tablename__ = "recommendations"
    __table_args__ = (
        UniqueConstraint("user_id", "exhibition_id", name="uq_reco_user_exhibition"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    exhibition_id: Mapped[int] = mapped_column(ForeignKey("exhibitions.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(255), nullable=False)


class Analytics(Base):
    """
    Key-value telemetric metrics and dimension store for the admin analytics dashboard.
    """
    __tablename__ = "analytics"

    id: Mapped[int] = mapped_column(primary_key=True)
    metric: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    dimensions: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
