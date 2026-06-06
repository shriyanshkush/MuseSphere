import base64, io, json, uuid
import qrcode
from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.models.entities import Booking, BookingStatus, Payment, PaymentStatus, Ticket
from app.schemas.dtos import BookingIn
PRICE_TABLE={'adult':300.0,'child':150.0,'student':200.0,'senior':180.0}; SLOT_CAPACITY=100
class BookingService:
    def __init__(self, db:Session): self.db=db
    def create_booking(self, user_id:int, data:BookingIn)->Booking:
        booked=self.db.scalar(select(func.coalesce(func.sum(Booking.visitor_count),0)).where(Booking.visit_date==data.visit_date, Booking.time_slot==data.time_slot, Booking.status!=BookingStatus.cancelled))
        if booked + data.visitor_count > SLOT_CAPACITY: raise HTTPException(409, 'Selected slot is full')
        booking=Booking(user_id=user_id, total_amount=PRICE_TABLE.get(data.ticket_type.lower(),300.0)*data.visitor_count, **data.model_dump())
        self.db.add(booking); self.db.commit(); self.db.refresh(booking); return booking
    def create_payment_order(self, booking_id:int):
        booking=self.db.get(Booking, booking_id)
        if not booking: raise HTTPException(404, 'Booking not found')
        order_id=f'order_{uuid.uuid4().hex[:16]}'
        self.db.add(Payment(booking_id=booking.id, provider_order_id=order_id, transaction_id=f'pending_{uuid.uuid4().hex[:12]}', amount=booking.total_amount)); self.db.commit()
        return {'order_id':order_id,'amount':booking.total_amount,'key_id':get_settings().razorpay_key_id}
    def verify_payment(self, booking_id:int, provider_order_id:str, transaction_id:str)->Payment:
        payment=self.db.scalar(select(Payment).where(Payment.booking_id==booking_id, Payment.provider_order_id==provider_order_id))
        if not payment: raise HTTPException(404, 'Payment order not found')
        payment.transaction_id=transaction_id; payment.status=PaymentStatus.paid
        booking=self.db.get(Booking, booking_id); booking.status=BookingStatus.confirmed
        if not self.db.scalar(select(Ticket).where(Ticket.booking_id==booking.id)): self.db.add(self.generate_ticket(booking))
        self.db.commit(); self.db.refresh(payment); return payment
    def generate_ticket(self, booking:Booking)->Ticket:
        payload=json.dumps({'booking_id':booking.id,'visitor_id':booking.user_id,'ticket_type':booking.ticket_type})
        img=qrcode.make(payload); buffer=io.BytesIO(); img.save(buffer, format='PNG')
        return Ticket(booking_id=booking.id, qr_payload=payload, qr_code_base64=base64.b64encode(buffer.getvalue()).decode())
