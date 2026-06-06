from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import require_admin
from app.database.session import get_db
from app.models.entities import Event, User
from app.repositories.domain import EventRepository
from app.schemas.dtos import EventIn, EventRead
router=APIRouter(prefix='/events', tags=['Events'])
@router.post('', response_model=EventRead, status_code=201)
def create(data:EventIn, db:Session=Depends(get_db), _:User=Depends(require_admin)): return EventRepository(db).add(Event(**data.model_dump()))
@router.get('', response_model=list[EventRead])
def list_items(db:Session=Depends(get_db)): return EventRepository(db).list(100,0)
@router.put('/{item_id}', response_model=EventRead)
def update(item_id:int, data:EventIn, db:Session=Depends(get_db), _:User=Depends(require_admin)):
    item=EventRepository(db).get(item_id)
    if not item: raise HTTPException(404, 'Event not found')
    for k,v in data.model_dump().items(): setattr(item,k,v)
    db.commit(); db.refresh(item); return item
@router.delete('/{item_id}', status_code=204)
def delete(item_id:int, db:Session=Depends(get_db), _:User=Depends(require_admin)):
    repo=EventRepository(db); item=repo.get(item_id)
    if not item: raise HTTPException(404, 'Event not found')
    repo.delete(item)
