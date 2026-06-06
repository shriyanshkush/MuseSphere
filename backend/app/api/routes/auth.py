from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.security import get_current_user
from app.database.session import get_db
from app.models.entities import User
from app.schemas.dtos import LoginRequest, TokenPair, UserCreate, UserRead
from app.services.auth import AuthService
router=APIRouter(prefix='/auth', tags=['Authentication'])
@router.post('/register', response_model=UserRead, status_code=201)
def register(data:UserCreate, db:Session=Depends(get_db)): return AuthService(db).register(data)
@router.post('/login', response_model=TokenPair)
def login(data:LoginRequest, db:Session=Depends(get_db)): return AuthService(db).login(data.email, data.password)
@router.post('/refresh', response_model=TokenPair)
def refresh(user:User=Depends(get_current_user), db:Session=Depends(get_db)): return AuthService(db).refresh_for(user)
@router.post('/logout')
def logout(): return {'detail':'Logout accepted. Client should discard tokens.'}
@router.get('/profile', response_model=UserRead)
def profile(user:User=Depends(get_current_user)): return user
