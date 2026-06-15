from app.backend.dependencies import get_current_user
from app.schemas.user import UserResponse
from fastapi import APIRouter
from typing import Annotated
from app.models.user import User
from fastapi import Depends, status

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_logged_user(user: Annotated[User, Depends(get_current_user)]):
    return user
