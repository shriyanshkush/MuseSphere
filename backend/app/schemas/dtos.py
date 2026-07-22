from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.entities import BookingStatus, PaymentStatus, UserRole


# --- Authentication & User Schemas ---

class UserCreate(BaseModel):
    """
    Data Transfer Object for registering a new user account.
    """
    name: str = Field(
        ...,
        min_length=2,
        max_length=120,
        description="Full legal or display name of the visitor",
        examples=["Aarav Sharma"]
    )
    email: EmailStr = Field(
        ...,
        description="Unique email address for authentication and ticket delivery",
        examples=["aarav.sharma@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Account password (at least 8 characters)",
        examples=["SecurePass!2026"]
    )


class UserRead(BaseModel):
    """
    Public representation of a registered user profile.
    """
    id: int = Field(..., description="Unique internal user identifier", examples=[1])
    name: str = Field(..., description="Visitor full name", examples=["Aarav Sharma"])
    email: EmailStr = Field(..., description="Registered email address", examples=["aarav.sharma@example.com"])
    role: UserRole = Field(..., description="User access privilege role", examples=[UserRole.visitor])
    language: str = Field(..., description="Preferred language code for AI interactions", examples=["en"])

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """
    Payload required for user login and JWT token issuance.
    """
    email: EmailStr = Field(..., description="Registered email address", examples=["aarav.sharma@example.com"])
    password: str = Field(..., description="Account password", examples=["SecurePass!2026"])


class TokenPair(BaseModel):
    """
    Pair of JSON Web Tokens issued upon successful login or refresh.
    """
    access_token: str = Field(..., description="Short-lived JWT access token for API authorization")
    refresh_token: str = Field(..., description="Long-lived JWT refresh token to mint new access tokens")
    token_type: str = Field(default="bearer", description="HTTP authorization token scheme")


# --- Exhibition Schemas ---

class ExhibitionIn(BaseModel):
    """
    Input schema for creating or updating a museum exhibition.
    """
    title: str = Field(..., min_length=3, max_length=160, description="Exhibition title", examples=["Ancient Civilizations"])
    description: str = Field(..., min_length=10, description="Detailed overview of what visitors will experience", examples=["Explore artifacts and stories from Mesopotamia, Egypt, and the Indus Valley."])
    category: str = Field(..., min_length=2, max_length=80, description="Classification tag", examples=["History"])
    location: str = Field(..., min_length=2, max_length=120, description="Gallery or hall identifier inside the museum", examples=["Gallery A - 1st Floor"])
    image: Optional[str] = Field(default=None, description="URL or asset path to the exhibition cover image", examples=["/assets/ancient.jpg"])
    timings: str = Field(default="10:00-18:00", description="Daily operating hours", examples=["10:00-18:00"])
    popularity_score: float = Field(default=0.0, ge=0.0, le=10.0, description="Popularity score index (0 to 10)", examples=[8.5])


class ExhibitionRead(ExhibitionIn):
    """
    Public representation of a museum exhibition.
    """
    id: int = Field(..., description="Unique exhibition identifier", examples=[101])

    model_config = ConfigDict(from_attributes=True)


# --- Event Schemas ---

class EventIn(BaseModel):
    """
    Input schema for scheduling a live museum event or workshop.
    """
    title: str = Field(..., min_length=3, max_length=160, description="Event or show title", examples=["Curator Talk: Modern Sculpture"])
    description: str = Field(..., min_length=10, description="Detailed event program summary", examples=["Join head curator Dr. Verma for an insightful walkthrough of 20th century sculptures."])
    event_type: str = Field(..., min_length=2, max_length=80, description="Type of event (Workshop, Guided Tour, Lecture)", examples=["Lecture"])
    starts_at: datetime = Field(..., description="ISO 8601 timestamp when the event commences", examples=["2026-08-15T14:30:00Z"])
    capacity: int = Field(default=50, ge=1, le=1000, description="Maximum attendees allowed", examples=[50])
    price: float = Field(default=0.0, ge=0.0, description="Ticket fee per person in INR (0 for free entry)", examples=[150.0])


class EventRead(EventIn):
    """
    Public representation of a scheduled event.
    """
    id: int = Field(..., description="Unique event identifier", examples=[201])

    model_config = ConfigDict(from_attributes=True)


# --- Booking & Ticket Schemas ---

class BookingIn(BaseModel):
    """
    Payload for reserving tickets for a visit slot.
    """
    visit_date: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Date of visit in YYYY-MM-DD format",
        examples=["2026-08-10"]
    )
    time_slot: str = Field(
        ...,
        description="Time slot window for entry",
        examples=["10:00"]
    )
    ticket_type: str = Field(
        default="adult",
        description="Ticket category (adult, child, student, senior)",
        examples=["adult"]
    )
    visitor_count: int = Field(
        default=1,
        ge=1,
        le=20,
        description="Number of visitors included in this booking (max 20 per group)",
        examples=[2]
    )


class BookingRead(BookingIn):
    """
    Detailed response representing a confirmed or pending ticket reservation.
    """
    id: int = Field(..., description="Unique booking reservation reference number", examples=[5001])
    user_id: int = Field(..., description="ID of the user who made the booking", examples=[1])
    total_amount: float = Field(..., description="Total price computed based on ticket rates and visitor count", examples=[600.0])
    status: BookingStatus = Field(..., description="Current status of the booking reservation", examples=[BookingStatus.pending_payment])

    model_config = ConfigDict(from_attributes=True)


# --- Payment Schemas ---

class PaymentOrderIn(BaseModel):
    """
    Request payload to initiate checkout for a booking.
    """
    booking_id: int = Field(..., description="ID of the booking requiring payment", examples=[5001])


class PaymentOrderOut(BaseModel):
    """
    Razorpay order configuration returned to the client for checkout initiation.
    """
    order_id: str = Field(..., description="Generated Razorpay/Gateway order identifier", examples=["order_rzp_demo_123456"])
    amount: float = Field(..., description="Amount payable in major currency units", examples=[600.0])
    currency: str = Field(default="INR", description="Three-letter ISO currency code", examples=["INR"])
    key_id: str = Field(..., description="Public Gateway Key ID for client SDK initialization", examples=["rzp_test_mock_key"])


class PaymentVerifyIn(BaseModel):
    """
    Payload containing gateway signature verification details after checkout completion.
    """
    booking_id: int = Field(..., description="ID of the booking being finalized", examples=[5001])
    provider_order_id: str = Field(..., description="Order ID returned from payment gateway", examples=["order_rzp_demo_123456"])
    transaction_id: str = Field(..., description="Payment transaction reference ID", examples=["pay_rzp_demo_987654"])
    signature: str = Field(default="demo-signature", description="Cryptographic verification signature", examples=["a1b2c3d4e5f6signature"])


class PaymentRead(BaseModel):
    """
    Completed payment transaction record.
    """
    id: int = Field(..., description="Internal payment record identifier", examples=[8001])
    booking_id: int = Field(..., description="Associated booking reservation identifier", examples=[5001])
    transaction_id: str = Field(..., description="Gateway transaction reference ID", examples=["pay_rzp_demo_987654"])
    provider_order_id: str = Field(..., description="Gateway order identifier", examples=["order_rzp_demo_123456"])
    amount: float = Field(..., description="Paid amount", examples=[600.0])
    status: PaymentStatus = Field(..., description="Final payment settlement status", examples=[PaymentStatus.paid])

    model_config = ConfigDict(from_attributes=True)


class TicketRead(BaseModel):
    """
    Digital QR code pass generated for entry after successful payment verification.
    """
    booking_id: int = Field(..., description="Booking reference associated with this ticket", examples=[5001])
    qr_payload: str = Field(..., description="Raw JSON data encoded inside the QR code", examples=['{"booking_id":5001,"visitor_id":1,"ticket_type":"adult"}'])
    qr_code_base64: str = Field(..., description="Base64-encoded PNG image of the QR code ready for display", examples=["iVBORw0KGgoAAAANSUhEUgAA..."])

    model_config = ConfigDict(from_attributes=True)


# --- AI Chatbot & RAG Knowledge Schemas ---

class ChatRequest(BaseModel):
    """
    Visitor prompt sent to the AI assistant.
    """
    message: str = Field(..., min_length=1, max_length=2000, description="User query or message text", examples=["Book 2 adult tickets for tomorrow at 10 AM."])
    language: Optional[str] = Field(default=None, description="Optional ISO language override code (en, hi, fr, es, de)", examples=["en"])


class ChatResponse(BaseModel):
    """
    Structured response generated by the LangGraph / Gemini AI agent workflow.
    """
    response: str = Field(..., description="AI conversational reply text", examples=["I can help book 2 adult tickets for tomorrow at 10:00 AM. That will be INR 600. Would you like me to create the booking slot now?"])
    intent: str = Field(..., description="Classified intent category (booking, recommendation, payment, knowledge, support)", examples=["booking"])
    language: str = Field(..., description="Language code in which the response was rendered", examples=["en"])


class KnowledgeQuery(BaseModel):
    """
    Query string for testing vector RAG similarity retrieval against uploaded documents.
    """
    query: str = Field(..., min_length=2, max_length=500, description="Search question or keyword phrase", examples=["What are the museum timing and holiday schedule?"])


# --- ML Recommendations & Sentiment Analysis Schemas ---

class RecommendationRead(BaseModel):
    """
    Personalized exhibition recommendation generated by the recommendation engine.
    """
    exhibition_id: int = Field(..., description="Exhibition identifier", examples=[101])
    title: str = Field(..., description="Exhibition title", examples=["Ancient Civilizations"])
    score: float = Field(..., description="Computed recommendation confidence score", examples=[10.5])
    reason: str = Field(..., description="Human-readable rationale for why this exhibit was suggested", examples=["Matched your history preference and high visitor ratings"])


class FeedbackIn(BaseModel):
    """
    Visitor feedback submission payload.
    """
    text: str = Field(..., min_length=3, max_length=2000, description="Review or feedback comments", examples=["The staff was extremely helpful and the QR ticketing made entry very smooth!"])


class FeedbackOut(BaseModel):
    """
    Sentiment classification output for submitted feedback.
    """
    sentiment: str = Field(..., description="Classified sentiment category (positive, neutral, negative)", examples=["positive"])
    score: float = Field(..., description="Normalized confidence score (-1.0 to +1.0 or 0.0 to 1.0)", examples=[0.85])
