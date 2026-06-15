from jose import jwt
from passlib.context import CryptContext
from app.backend.config import settings
from datetime import datetime, timezone, timedelta


crypt_context = CryptContext(schemes=["argon2"],deprecated="auto")





def get_password_hash(password: str) -> str:
    return crypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return crypt_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRES_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.ACCESS_TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRES_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.REFRESH_TOKEN_SECRET_KEY, algorithm=settings.ALGORITHM)