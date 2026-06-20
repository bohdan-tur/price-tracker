from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from app.backend.dependencies import db_dependency,get_current_user
from app.backend.security import get_password_hash
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from typing import Annotated
from fastapi import Depends
from app.backend.security import verify_password,create_access_token,create_refresh_token
from app.schemas.refresh_token import RefreshTokenRequest
from jose import jwt,ExpiredSignatureError,JWTError
from app.backend.config import settings

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

     access_token = create_access_token(data={"sub": str(user.id)})
     refresh_token = create_refresh_token(data={"sub": str(user.id)})
     return {"access_token": access_token,
             "refresh_token": refresh_token,
             "token_type": "bearer"

             }




@router.post("/refresh_token")
async def refresh_token(request_data: RefreshTokenRequest, db: db_dependency):

    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail = "Could not validate credentials",
                                          headers = {"WWW-Authenticate":"Bearer"}
                                          )

    try:

        payload = jwt.decode(
            request_data.refresh_token,
            settings.REFRESH_TOKEN_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id_str : str = payload.get("sub")

        if not user_id_str:
            raise credentials_exception

        user_id = int(user_id_str)

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token has expired")

    except (JWTError,ValueError):
        raise credentials_exception



    query = await db.execute(select(User).where(User.id == user_id))
    user = query.scalar_one_or_none()
    if not user:
        raise credentials_exception


    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Inactive user account")


    new_access_token = create_access_token(data = {"sub": str(user.id)})

    return {"access_token": new_access_token,
            "token_type": "bearer"}











