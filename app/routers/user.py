from app.backend.dependencies import get_current_user, db_dependency, get_current_superuser
from app.schemas.user import UserResponse
from fastapi import APIRouter, HTTPException
from typing import Annotated
from app.models.user import User
from fastapi import Depends, status,Query
from app.schemas.password_change import PasswordChangeSchema
from app.backend.security import verify_password, get_password_hash
from sqlalchemy import select

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_current_logged_user(user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return user


@router.patch("/me/password", status_code=status.HTTP_200_OK)
async def change_password(user: Annotated[User, Depends(get_current_user)], password_change: PasswordChangeSchema,
                          db: db_dependency) -> dict:
    if not verify_password(password_change.old_password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid old password")

    user.hashed_password = get_password_hash(password_change.new_password)
    await db.commit()

    return {"msg": "Password updated successfully"}


@router.delete("/me/", status_code=status.HTTP_200_OK)
async def delete_my_account(user: Annotated[User, Depends(get_current_user)], db: db_dependency) -> dict:
    user.is_active = False
    await db.commit()
    return {"msg": "User deactivated successfully"}


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[UserResponse], dependencies=[Depends(get_current_superuser)])
async def get_all_users(
    db: db_dependency,
    limit: Annotated[int, Query( ge=1, le=100, description="Number of users to return")] = 10,
    offset: Annotated[int, Query( ge=0, description="Number of users to skip")] = 0
) -> list[UserResponse]:
    query = await db.execute(select(User).offset(offset).limit(limit))
    return query.scalars().all()

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=UserResponse, dependencies=[Depends(get_current_superuser)])
async def get_user_by_id(
        user_id: int,
        db: db_dependency
) -> UserResponse:
    query = await db.execute(select(User).where(User.id == user_id))
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.patch("/{user_id}/status", status_code=status.HTTP_200_OK, response_model=dict, dependencies=[Depends(get_current_superuser)])
async def update_user_status(
        user_id: int,
        db: db_dependency
) -> dict:
    query = await db.execute(select(User).where(User.id == user_id))
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_superuser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change status of a superuser")

    user.is_active = False
    await db.commit()
    return {"msg": f"User {user_id} disabled successfully"}


@router.delete("/{user_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(get_current_superuser)])
async def delete_user_hard(user_id: int, db: db_dependency) -> dict:
    query = await db.execute(select(User).where(User.id == user_id))
    user = query.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user.is_superuser:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete a superuser")

    await db.delete(user)
    await db.commit()
    return {"msg": f"User {user_id}  was  deleted"}
