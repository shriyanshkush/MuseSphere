from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import BookingStatus, User
from app.repositories.domain import BookingRepository
from app.schemas.dtos import BookingIn, BookingRead
from app.services.booking import BookingService
router=APIRouter(prefix='/bookings', tags=['Bookings'])
@router.post('', response_model=BookingRead, status_code=201)
def create(data:BookingIn, user:User=Depends(get_current_user), db:Session=Depends(get_db)): return BookingService(db).create_booking(user.id, data)
@router.get('', response_model=list[BookingRead])
def list_items(user:User=Depends(get_current_user), db:Session=Depends(get_db)): return BookingRepository(db).for_user(user.id)
@router.get('/{booking_id}', response_model=BookingRead)
def get_item(booking_id:int, user:User=Depends(get_current_user), db:Session=Depends(get_db)):
    item=BookingRepository(db).get(booking_id)
    if not item or item.user_id != user.id: raise HTTPException(404, 'Booking not found')
    return item
@router.delete('/{booking_id}', status_code=204)
def cancel(booking_id:int, user:User=Depends(get_current_user), db:Session=Depends(get_db)):
    item=BookingRepository(db).get(booking_id)
    if not item or item.user_id != user.id: raise HTTPException(404, 'Booking not found')
    item.status=BookingStatus.cancelled; db.commit()
