from sqlalchemy import select
from sqlalchemy.orm import Session
class Repository:
    def __init__(self, db:Session, model): self.db=db; self.model=model
    def get(self, item_id:int): return self.db.get(self.model, item_id)
    def list(self, limit:int=20, offset:int=0): return self.db.scalars(select(self.model).limit(limit).offset(offset)).all()
    def add(self, obj): self.db.add(obj); self.db.commit(); self.db.refresh(obj); return obj
    def delete(self, obj): self.db.delete(obj); self.db.commit()
from app.models.entities import User, Exhibition, Event, Booking, Payment, Ticket, ChatHistory, KnowledgeDocument, Feedback
class UserRepository(Repository):
    def __init__(self, db): super().__init__(db, User)
    def by_email(self, email): return self.db.scalar(select(User).where(User.email==email))
class ExhibitionRepository(Repository):
    def __init__(self, db): super().__init__(db, Exhibition)
class EventRepository(Repository):
    def __init__(self, db): super().__init__(db, Event)
class BookingRepository(Repository):
    def __init__(self, db): super().__init__(db, Booking)
    def for_user(self, user_id): return self.db.scalars(select(Booking).where(Booking.user_id==user_id)).all()
class PaymentRepository(Repository):
    def __init__(self, db): super().__init__(db, Payment)
class TicketRepository(Repository):
    def __init__(self, db): super().__init__(db, Ticket)
class ChatRepository(Repository):
    def __init__(self, db): super().__init__(db, ChatHistory)
    def history(self, user_id): return self.db.scalars(select(ChatHistory).where(ChatHistory.user_id==user_id).order_by(ChatHistory.created_at.desc())).all()
class KnowledgeRepository(Repository):
    def __init__(self, db): super().__init__(db, KnowledgeDocument)
class FeedbackRepository(Repository):
    def __init__(self, db): super().__init__(db, Feedback)
