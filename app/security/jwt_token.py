import os
import jwt
from jwt.exceptions import InvalidTokenError
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status
from app.schemas.response_schemas import TokenData

load_dotenv()


SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 1500


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenData | HTTPException:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise credentials_exception
        return TokenData(user_email=user_email)
    except InvalidTokenError:
        raise credentials_exception