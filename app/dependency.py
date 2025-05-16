from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from app.config.database import get_db
from sqlalchemy.orm import Session
from app.service.user_service import UserService
from app.security.jwt_token import decode_access_token

DATABASE_OBJECT = Annotated[Session, Depends(get_db)]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login")

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: DATABASE_OBJECT):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    _service = UserService(db)
    user = _service.get_current_user(token_data.user_email)
    if user is None:
        raise credentials_exception
    return user