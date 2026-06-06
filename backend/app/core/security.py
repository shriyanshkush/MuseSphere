from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.config import get_settings
from app.database.session import get_db
from app.models.entities import User, UserRole
pwd_context=CryptContext(schemes=['bcrypt'], deprecated='auto'); oauth2_scheme=OAuth2PasswordBearer(tokenUrl='/auth/login')
def hash_password(password:str)->str: return pwd_context.hash(password)
def verify_password(password:str, hashed_password:str)->bool: return pwd_context.verify(password, hashed_password)
def create_token(subject:str, minutes:int, token_type:str='access')->str:
    s=get_settings(); return jwt.encode({'sub':subject,'type':token_type,'exp':datetime.now(timezone.utc)+timedelta(minutes=minutes)}, s.jwt_secret, algorithm=s.jwt_algorithm)
def get_current_user(token:str=Depends(oauth2_scheme), db:Session=Depends(get_db))->User:
    s=get_settings(); err=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid credentials')
    try: user_id=int(jwt.decode(token, s.jwt_secret, algorithms=[s.jwt_algorithm]).get('sub','0'))
    except (JWTError, ValueError): raise err
    user=db.get(User, user_id)
    if not user or not user.is_active: raise err
    return user
def require_admin(user:User=Depends(get_current_user))->User:
    if user.role != UserRole.admin: raise HTTPException(status_code=403, detail='Admin role required')
    return user
