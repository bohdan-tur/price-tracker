from fastapi.security import OAuth2PasswordBearer
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends,HTTPException
from .db import get_session
from app.backend.config import settings
from jose import jwt,JWTError
from app.models.user import User
from sqlalchemy import select
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

db_dependency = Annotated[AsyncSession,Depends(get_session)]


async def get_current_user(db:db_dependency,token:Annotated[str,Depends(oauth2_scheme)]):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token,settings.ACCESS_TOKEN_SECRET_KEY,algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
            raise credentials_exception

    query = await db.execute(select(User).where(User.email == email))
    user = query.scalar_one_or_none()
    if user is None:
        raise credentials_exception

    if not  user.is_active:
        raise HTTPException(status_code=403,detail="Inactive user account")

    return user





async def get_current_superuser(user:Annotated[User,Depends(get_current_user)]):
    if not user.is_superuser:
        raise HTTPException(status_code=403,detail="Not enough permissions")
    return user