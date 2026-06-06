from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.security import require_admin
from app.database.session import get_db
from app.models.entities import Exhibition, User
from app.repositories.domain import ExhibitionRepository
from app.schemas.dtos import ExhibitionIn, ExhibitionRead
router=APIRouter(prefix='/exhibitions', tags=['Exhibitions'])
@router.post('', response_model=ExhibitionRead, status_code=201)
def create(data:ExhibitionIn, db:Session=Depends(get_db), _:User=Depends(require_admin)): return ExhibitionRepository(db).add(Exhibition(**data.model_dump()))
@router.get('', response_model=list[ExhibitionRead])
def list_items(limit:int=Query(20, ge=1, le=100), offset:int=Query(0, ge=0), db:Session=Depends(get_db)): return ExhibitionRepository(db).list(limit, offset)
@router.get('/{item_id}', response_model=ExhibitionRead)
def get_item(item_id:int, db:Session=Depends(get_db)):
    item=ExhibitionRepository(db).get(item_id)
    if not item: raise HTTPException(404, 'Exhibition not found')
    return item
@router.put('/{item_id}', response_model=ExhibitionRead)
def update(item_id:int, data:ExhibitionIn, db:Session=Depends(get_db), _:User=Depends(require_admin)):
    item=ExhibitionRepository(db).get(item_id)
    if not item: raise HTTPException(404, 'Exhibition not found')
    for key,value in data.model_dump().items(): setattr(item,key,value)
    db.commit(); db.refresh(item); return item
@router.delete('/{item_id}', status_code=204)
def delete(item_id:int, db:Session=Depends(get_db), _:User=Depends(require_admin)):
    repo=ExhibitionRepository(db); item=repo.get(item_id)
    if not item: raise HTTPException(404, 'Exhibition not found')
    repo.delete(item)
