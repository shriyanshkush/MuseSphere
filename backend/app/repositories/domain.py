from typing import Any, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import (
    Booking,
    ChatHistory,
    Event,
    Exhibition,
    Feedback,
    KnowledgeDocument,
    Payment,
    Ticket,
    User,
)

ModelType = TypeVar("ModelType")


class Repository(Generic[ModelType]):
    """
    Generic asynchronous CRUD repository over SQLAlchemy AsyncSession.
    """
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model

    async def get(self, item_id: int) -> Optional[ModelType]:
        """Fetch a single entity by primary key ID."""
        return await self.db.get(self.model, item_id)

    async def list(self, limit: int = 20, offset: int = 0) -> List[ModelType]:
        """List entities with pagination parameters."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.db.scalars(stmt)
        return list(result.all())

    async def add(self, obj: ModelType) -> ModelType:
        """Persist a new entity instance and refresh from database."""
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """Delete an existing entity instance."""
        await self.db.delete(obj)
        await self.db.commit()


class UserRepository(Repository[User]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)

    async def by_email(self, email: str) -> Optional[User]:
        """Fetch a user exactly matching the provided email address."""
        stmt = select(User).where(User.email == email)
        return await self.db.scalar(stmt)


class ExhibitionRepository(Repository[Exhibition]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Exhibition)


class EventRepository(Repository[Event]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Event)


class BookingRepository(Repository[Booking]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Booking)

    async def for_user(self, user_id: int) -> List[Booking]:
        """List all ticket bookings associated with a given user ID, newest first."""
        stmt = select(Booking).where(Booking.user_id == user_id).order_by(Booking.created_at.desc())
        result = await self.db.scalars(stmt)
        return list(result.all())


class PaymentRepository(Repository[Payment]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Payment)


class TicketRepository(Repository[Ticket]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Ticket)

    async def by_booking(self, booking_id: int) -> Optional[Ticket]:
        """Fetch the ticket associated with a booking ID."""
        stmt = select(Ticket).where(Ticket.booking_id == booking_id)
        return await self.db.scalar(stmt)


class ChatRepository(Repository[ChatHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, ChatHistory)

    async def history(self, user_id: int) -> List[ChatHistory]:
        """Fetch chronological conversation logs for a given user."""
        stmt = select(ChatHistory).where(ChatHistory.user_id == user_id).order_by(ChatHistory.created_at.desc())
        result = await self.db.scalars(stmt)
        return list(result.all())


class KnowledgeRepository(Repository[KnowledgeDocument]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, KnowledgeDocument)


class FeedbackRepository(Repository[Feedback]):
    def __init__(self, db: AsyncSession):
        super().__init__(db, Feedback)
