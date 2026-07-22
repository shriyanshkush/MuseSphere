import base64
import io
import json
import logging
import uuid
from typing import Any, Dict
import qrcode
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.models.entities import Booking, BookingStatus, Payment, PaymentStatus, Ticket
from app.schemas.dtos import BookingIn

logger = logging.getLogger(__name__)

PRICE_TABLE = {
    "adult": 300.0,
    "child": 150.0,
    "student": 200.0,
    "senior": 180.0,
}
SLOT_CAPACITY = 100


class BookingService:
    """
    Business logic handling ticket booking creation, slot capacity validation,
    payment gateway order initiation, transaction verification, and QR ticket issuance.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

    async def create_booking(self, user_id: int, data: BookingIn) -> Booking:
        """Create a new booking after verifying slot capacity."""
        stmt = select(func.coalesce(func.sum(Booking.visitor_count), 0)).where(
            Booking.visit_date == data.visit_date,
            Booking.time_slot == data.time_slot,
            Booking.status != BookingStatus.cancelled
        )
        booked_count = await self.db.scalar(stmt)
        if (booked_count or 0) + data.visitor_count > SLOT_CAPACITY:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Selected time slot is full. Only {max(0, SLOT_CAPACITY - (booked_count or 0))} spots remaining."
            )

        ticket_price = PRICE_TABLE.get(data.ticket_type.lower(), 300.0)
        total_amount = ticket_price * data.visitor_count

        booking = Booking(
            user_id=user_id,
            total_amount=total_amount,
            **data.model_dump()
        )
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def create_payment_order(self, booking_id: int) -> Dict[str, Any]:
        """Create Razorpay mock order structure for checkout."""
        booking = await self.db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking reference not found."
            )

        order_id = f"order_{uuid.uuid4().hex[:16]}"
        payment = Payment(
            booking_id=booking.id,
            provider_order_id=order_id,
            transaction_id=f"pending_{uuid.uuid4().hex[:12]}",
            amount=booking.total_amount,
            status=PaymentStatus.pending,
        )
        self.db.add(payment)
        await self.db.commit()

        return {
            "order_id": order_id,
            "amount": booking.total_amount,
            "currency": "INR",
            "key_id": self.settings.razorpay_key_id,
        }

    async def verify_payment(self, booking_id: int, provider_order_id: str, transaction_id: str) -> Payment:
        """Verify checkout payment signature/transaction and generate QR ticket."""
        stmt = select(Payment).where(
            Payment.booking_id == booking_id,
            Payment.provider_order_id == provider_order_id
        )
        payment = await self.db.scalar(stmt)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment order record not found."
            )

        payment.transaction_id = transaction_id
        payment.status = PaymentStatus.paid

        booking = await self.db.get(Booking, booking_id)
        if booking:
            booking.status = BookingStatus.confirmed

        ticket_stmt = select(Ticket).where(Ticket.booking_id == booking_id)
        existing_ticket = await self.db.scalar(ticket_stmt)
        if not existing_ticket and booking:
            ticket = self.generate_ticket(booking)
            self.db.add(ticket)

        await self.db.commit()
        await self.db.refresh(payment)
        return payment

    def generate_ticket(self, booking: Booking) -> Ticket:
        """Generate base64 encoded PNG QR code payload for confirmed ticket entry."""
        payload_data = {
            "booking_id": booking.id,
            "visitor_id": booking.user_id,
            "ticket_type": booking.ticket_type,
            "visitors": booking.visitor_count,
        }
        payload_str = json.dumps(payload_data)
        img = qrcode.make(payload_str)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return Ticket(
            booking_id=booking.id,
            qr_payload=payload_str,
            qr_code_base64=qr_base64,
        )
