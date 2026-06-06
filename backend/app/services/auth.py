from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.core.security import create_token, hash_password, verify_password
from app.models.entities import User
from app.repositories.domain import UserRepository
from app.schemas.dtos import UserCreate
class AuthService:
    def __init__(self, db:Session): self.repo=UserRepository(db); self.settings=get_settings()
    def register(self, data:UserCreate)->User:
        if self.repo.by_email(data.email): raise HTTPException(409, 'Email already registered')
        return self.repo.add(User(name=data.name, email=data.email, hashed_password=hash_password(data.password)))
    def login(self, email:str, password:str):
        user=self.repo.by_email(email)
        if not user or not verify_password(password, user.hashed_password): raise HTTPException(401, 'Invalid email or password')
        return {'access_token':create_token(str(user.id), self.settings.access_token_minutes), 'refresh_token':create_token(str(user.id), self.settings.refresh_token_minutes, 'refresh')}
    def refresh_for(self, user:User): return {'access_token':create_token(str(user.id), self.settings.access_token_minutes), 'refresh_token':create_token(str(user.id), self.settings.refresh_token_minutes, 'refresh')}
