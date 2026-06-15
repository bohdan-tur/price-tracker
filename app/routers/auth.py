from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from app.backend.dependencies import db_dependency
from app.backend.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from typing import Annotated
from fastapi import Depends
from app.backend.security import verify_password,create_access_token,create_refresh_token
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: db_dependency):
      query = await db.execute(select(User).where(User.email == user_data.email))
      existing_user = query.scalar_one_or_none()
      if existing_user:
            raise HTTPException(status_code=400, detail="User already exists")

      hashed_password = get_password_hash(user_data.password)
      new_user = User(email=user_data.email, hashed_password=hashed_password)
      db.add(new_user)
      await db.commit()
      await db.refresh(new_user)
      return new_user

@router.post("/login")
async def login(form_data:Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
     query = await db.execute(select(User).where(User.email == form_data.username))
     user = query.scalar_one_or_none()
     if not user:
         raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Incorrect email or password",
             headers={"WWW-Authenticate": "Bearer"},
         )
     if not verify_password(form_data.password, user.hashed_password):
         raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Incorrect password",
             headers={"WWW-Authenticate": "Bearer"},
         )

     access_token = create_access_token(data={"sub": user.email})
     refresh_token = create_refresh_token(data={"sub": user.email})
     return {"access_token": access_token,
             "refresh_token": refresh_token,
             "token_type": "bearer"

             }


