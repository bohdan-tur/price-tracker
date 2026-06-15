from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.schemas.item import ItemCreate, ItemResponse
from app.backend.dependencies import db_dependency, get_current_user
from app.models.item import Item
from app.models.user import User

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/",response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate,
    db: db_dependency,
    user: User = Depends(get_current_user)
):
    new_item = Item(
        title=item.title,
        url=str(item.url),
        current_price=None,
        user_id=user.id
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    query = await db.execute(
        select(Item)
        .where(Item.id == new_item.id)
        .options(selectinload(Item.price_histories))
    )
    return query.scalar_one()


@router.get("/", response_model=List[ItemResponse],status_code=status.HTTP_200_OK)
async def get_my_items(
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    query = await db.execute(
        select(Item)
        .where(Item.user_id == current_user.id)
        .options(selectinload(Item.price_histories))
    )
    return query.scalars().all()


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: db_dependency,
    current_user: User = Depends(get_current_user)
):
    query = await db.execute(
        select(Item).where(Item.id == item_id, Item.user_id == current_user.id)
    )
    item = query.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found"
        )

    await db.delete(item)
    await db.commit()





