from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.backend.dependencies import db_dependency, get_current_user
from app.backend.scraper import get_current_price
from app.models.item import Item
from app.models.price_history import PriceHistory
from app.models.user import User
from app.schemas.item import ItemCreate, ItemResponse

router = APIRouter(prefix="/items", tags=["items"])


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: ItemCreate, db: db_dependency, user: User = Depends(get_current_user)
) -> ItemResponse:
    fetched_price = await get_current_price(str(item.url))

    new_item = Item(
        title=item.title,
        url=str(item.url),
        current_price=fetched_price,
        user_id=user.id,
    )
    db.add(new_item)
    await db.flush()
    saved_item_id = new_item.id

    if fetched_price is not None:
        history_record = PriceHistory(item_id=new_item.id, price=fetched_price)
        db.add(history_record)

        await db.commit()

    query = await db.execute(
        select(Item)
        .where(Item.id == saved_item_id)
        .options(selectinload(Item.price_histories))
    )
    return query.scalar_one()


@router.get("/", response_model=list[ItemResponse], status_code=status.HTTP_200_OK)
async def get_my_items(
    db: db_dependency,
    current_user: User = Depends(get_current_user),
    limit: Annotated[
        int, Query(ge=1, le=100, description="Number of items to return")
    ] = 10,
    offset: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
) -> list[ItemResponse]:
    query = await db.execute(
        select(Item)
        .where(Item.user_id == current_user.id)
        .options(selectinload(Item.price_histories))
        .limit(limit)
        .offset(offset)
    )
    return query.scalars().all()


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int, db: db_dependency, current_user: User = Depends(get_current_user)
) -> None:
    query = await db.execute(
        select(Item).where(Item.id == item_id, Item.user_id == current_user.id)
    )
    item = query.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )

    await db.delete(item)
    await db.commit()
