from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from app.models.entities import BookingStatus, PaymentStatus, UserRole
class UserCreate(BaseModel): name:str=Field(min_length=2,max_length=120); email:EmailStr; password:str=Field(min_length=8)
class UserRead(BaseModel): id:int; name:str; email:EmailStr; role:UserRole; language:str; model_config={'from_attributes':True}
class LoginRequest(BaseModel): email:EmailStr; password:str
class TokenPair(BaseModel): access_token:str; refresh_token:str; token_type:str='bearer'
class ExhibitionIn(BaseModel): title:str; description:str; category:str; location:str; image:str|None=None; timings:str='10:00-18:00'; popularity_score:float=0
class ExhibitionRead(ExhibitionIn): id:int; model_config={'from_attributes':True}
class EventIn(BaseModel): title:str; description:str; event_type:str; starts_at:datetime; capacity:int=Field(ge=1); price:float=Field(ge=0)
class EventRead(EventIn): id:int; model_config={'from_attributes':True}
class BookingIn(BaseModel): visit_date:str; time_slot:str; ticket_type:str='adult'; visitor_count:int=Field(ge=1, le=20)
class BookingRead(BookingIn): id:int; user_id:int; total_amount:float; status:BookingStatus; model_config={'from_attributes':True}
class PaymentOrderIn(BaseModel): booking_id:int
class PaymentOrderOut(BaseModel): order_id:str; amount:float; currency:str='INR'; key_id:str
class PaymentVerifyIn(BaseModel): booking_id:int; provider_order_id:str; transaction_id:str; signature:str='demo-signature'
class PaymentRead(BaseModel): id:int; booking_id:int; transaction_id:str; provider_order_id:str; amount:float; status:PaymentStatus; model_config={'from_attributes':True}
class TicketRead(BaseModel): booking_id:int; qr_payload:str; qr_code_base64:str; model_config={'from_attributes':True}
class ChatRequest(BaseModel): message:str; language:str|None=None
class ChatResponse(BaseModel): response:str; intent:str; language:str
class KnowledgeQuery(BaseModel): query:str
class RecommendationRead(BaseModel): exhibition_id:int; title:str; score:float; reason:str
class FeedbackIn(BaseModel): text:str=Field(min_length=3)
class FeedbackOut(BaseModel): sentiment:str; score:float
