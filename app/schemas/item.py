from pydantic import BaseModel, HttpUrl
from app.schemas.price_history import PriceHistoryResponse
class ItemBase(BaseModel):
    title: str
    url: HttpUrl

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    current_price: float | None
    user_id: int
    price_histories: list[PriceHistoryResponse] = []


    class Config:
        from_attributes = True