from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import Payment, User
from app.schemas.dtos import PaymentOrderIn, PaymentOrderOut, PaymentRead, PaymentVerifyIn
from app.services.booking import BookingService

router = APIRouter(prefix="/payments", tags=["Payments Gateway Integration"])


@router.post(
    "/create-order",
    response_model=PaymentOrderOut,
    summary="Initiate Razorpay checkout order",
    description="Creates a Gateway order payload for an existing pending booking. Returns order ID and public API key required by client SDKs to render payment modal.",
    response_description="Order initiation details.",
    responses={
        401: {"description": "Authentication required."},
        404: {"description": "Associated booking ID not found."}
    }
)
async def create_order(
    data: PaymentOrderIn,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Create a new payment gateway checkout order."""
    return await BookingService(db).create_payment_order(data.booking_id)


@router.post(
    "/verify",
    response_model=PaymentRead,
    summary="Verify payment settlement and issue QR ticket",
    description="Validates gateway transaction signature after checkout, marks the payment as settled, confirms the booking status, and automatically issues a digital QR ticket pass.",
    response_description="Completed payment settlement record.",
    responses={
        401: {"description": "Authentication required."},
        404: {"description": "Payment order record not found."}
    }
)
async def verify(
    data: PaymentVerifyIn,
    _: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Payment:
    """Verify transaction signature and finalize booking."""
    return await BookingService(db).verify_payment(
        data.booking_id,
        data.provider_order_id,
        data.transaction_id,
    )
