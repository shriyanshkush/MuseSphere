from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import User
from app.schemas.dtos import PaymentOrderIn, PaymentOrderOut, PaymentRead, PaymentVerifyIn
from app.services.booking import BookingService
router=APIRouter(prefix='/payments', tags=['Payments'])
@router.post('/create-order', response_model=PaymentOrderOut)
def create_order(data:PaymentOrderIn, _:User=Depends(get_current_user), db:Session=Depends(get_db)): return BookingService(db).create_payment_order(data.booking_id)
@router.post('/verify', response_model=PaymentRead)
def verify(data:PaymentVerifyIn, _:User=Depends(get_current_user), db:Session=Depends(get_db)): return BookingService(db).verify_payment(data.booking_id, data.provider_order_id, data.transaction_id)
