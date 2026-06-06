import enum
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base
class UserRole(str, enum.Enum): visitor='visitor'; admin='admin'
class PaymentStatus(str, enum.Enum): pending='pending'; paid='paid'; failed='failed'; refunded='refunded'
class BookingStatus(str, enum.Enum): pending_payment='pending_payment'; confirmed='confirmed'; cancelled='cancelled'
class User(Base):
    __tablename__='users'; id:Mapped[int]=mapped_column(primary_key=True); name:Mapped[str]=mapped_column(String(120)); email:Mapped[str]=mapped_column(String(255), unique=True, index=True); hashed_password:Mapped[str]=mapped_column(String(255)); role:Mapped[UserRole]=mapped_column(Enum(UserRole), default=UserRole.visitor); language:Mapped[str]=mapped_column(String(12), default='en'); is_active:Mapped[bool]=mapped_column(Boolean, default=True); created_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class Exhibition(Base):
    __tablename__='exhibitions'; id:Mapped[int]=mapped_column(primary_key=True); title:Mapped[str]=mapped_column(String(160), index=True); description:Mapped[str]=mapped_column(Text); category:Mapped[str]=mapped_column(String(80), index=True); location:Mapped[str]=mapped_column(String(120)); image:Mapped[str|None]=mapped_column(String(500), nullable=True); timings:Mapped[str]=mapped_column(String(120), default='10:00-18:00'); popularity_score:Mapped[float]=mapped_column(Float, default=0.0)
class Event(Base):
    __tablename__='events'; id:Mapped[int]=mapped_column(primary_key=True); title:Mapped[str]=mapped_column(String(160)); description:Mapped[str]=mapped_column(Text); event_type:Mapped[str]=mapped_column(String(80)); starts_at:Mapped[datetime]=mapped_column(DateTime); capacity:Mapped[int]=mapped_column(Integer, default=50); price:Mapped[float]=mapped_column(Float, default=0.0)
class Booking(Base):
    __tablename__='bookings'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id')); visit_date:Mapped[str]=mapped_column(String(20), index=True); time_slot:Mapped[str]=mapped_column(String(20), index=True); ticket_type:Mapped[str]=mapped_column(String(60)); visitor_count:Mapped[int]=mapped_column(Integer); total_amount:Mapped[float]=mapped_column(Float); status:Mapped[BookingStatus]=mapped_column(Enum(BookingStatus), default=BookingStatus.pending_payment); created_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow); user:Mapped[User]=relationship()
class Payment(Base):
    __tablename__='payments'; id:Mapped[int]=mapped_column(primary_key=True); booking_id:Mapped[int]=mapped_column(ForeignKey('bookings.id')); transaction_id:Mapped[str]=mapped_column(String(120), unique=True); provider_order_id:Mapped[str]=mapped_column(String(120), unique=True); amount:Mapped[float]=mapped_column(Float); status:Mapped[PaymentStatus]=mapped_column(Enum(PaymentStatus), default=PaymentStatus.pending); created_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class Ticket(Base):
    __tablename__='tickets'; id:Mapped[int]=mapped_column(primary_key=True); booking_id:Mapped[int]=mapped_column(ForeignKey('bookings.id'), unique=True); qr_payload:Mapped[str]=mapped_column(Text); qr_code_base64:Mapped[str]=mapped_column(Text); issued_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class ChatHistory(Base):
    __tablename__='chat_history'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id')); message:Mapped[str]=mapped_column(Text); response:Mapped[str]=mapped_column(Text); language:Mapped[str]=mapped_column(String(12), default='en'); created_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class KnowledgeDocument(Base):
    __tablename__='knowledge_documents'; id:Mapped[int]=mapped_column(primary_key=True); filename:Mapped[str]=mapped_column(String(255)); content:Mapped[str]=mapped_column(Text); chunks:Mapped[dict]=mapped_column(JSON, default=dict); created_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class Feedback(Base):
    __tablename__='feedback'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int|None]=mapped_column(ForeignKey('users.id'), nullable=True); text:Mapped[str]=mapped_column(Text); sentiment:Mapped[str]=mapped_column(String(20)); score:Mapped[float]=mapped_column(Float); created_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class Recommendation(Base):
    __tablename__='recommendations'; id:Mapped[int]=mapped_column(primary_key=True); user_id:Mapped[int]=mapped_column(ForeignKey('users.id')); exhibition_id:Mapped[int]=mapped_column(ForeignKey('exhibitions.id')); score:Mapped[float]=mapped_column(Float); reason:Mapped[str]=mapped_column(String(255)); __table_args__=(UniqueConstraint('user_id','exhibition_id', name='uq_reco_user_exhibition'),)
class Analytics(Base):
    __tablename__='analytics'; id:Mapped[int]=mapped_column(primary_key=True); metric:Mapped[str]=mapped_column(String(80), index=True); value:Mapped[float]=mapped_column(Float); dimensions:Mapped[dict]=mapped_column(JSON, default=dict); recorded_at:Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
