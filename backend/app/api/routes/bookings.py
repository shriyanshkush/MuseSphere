from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import Booking, BookingStatus, User
from app.repositories.domain import BookingRepository
from app.schemas.dtos import BookingIn, BookingRead
from app.services.booking import BookingService

router = APIRouter(prefix="/bookings", tags=["Ticket Bookings"])


@router.post(
    "",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
    summary="Reserve tickets for a museum visit slot",
    description="Validates slot capacity (max 100 visitors per slot) and creates a new ticket reservation with computed pricing.",
    response_description="Created booking details with pending payment status.",
    responses={
        401: {"description": "Authentication required."},
        409: {"description": "Selected time slot is full or exceeds remaining capacity."},
        422: {"description": "Invalid visit date, slot window, or visitor count out of bounds."}
    }
)
async def create(
    data: BookingIn,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Booking:
    """Create a new museum ticket booking."""
    return await BookingService(db).create_booking(user.id, data)


@router.get(
    "",
    response_model=List[BookingRead],
    summary="List bookings for current visitor",
    description="Returns all ticket reservations (pending, confirmed, and cancelled) associated with the authenticated visitor, ordered from newest to oldest.",
    response_description="Array of booking reservation records."
)
async def list_items(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Booking]:
    """Retrieve all bookings belonging to the active user."""
    return await BookingRepository(db).for_user(user.id)


@router.get(
    "/{booking_id}",
    response_model=BookingRead,
    summary="Retrieve specific booking details",
    description="Fetches detailed pricing, status, and visitor count for a specific booking ID owned by the caller.",
    response_description="Booking reservation object.",
    responses={
        404: {"description": "Booking reference not found or does not belong to user."}
    }
)
async def get_item(
    booking_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Booking:
    """Get single booking details."""
    item = await BookingRepository(db).get(booking_id)
    if not item or item.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking reservation not found."
        )
    return item


@router.delete(
    "/{booking_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel a booking reservation",
    description="Marks a pending or confirmed booking reservation as cancelled. Freeing up slot capacity for other visitors.",
    responses={
        404: {"description": "Booking reference not found or unauthorized."}
    }
)
async def cancel(
    booking_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Cancel user booking reservation."""
    item = await BookingRepository(db).get(booking_id)
    if not item or item.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking reservation not found."
        )
    item.status = BookingStatus.cancelled
    await db.commit()
