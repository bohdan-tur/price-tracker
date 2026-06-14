from datetime import datetime
from pydantic import BaseModel

class PriceHistoryResponse(BaseModel):
    id: int
    price: float
    recorded_at: datetime

    class Config:
        from_attributes = True