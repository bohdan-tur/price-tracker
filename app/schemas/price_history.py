from datetime import datetime
from pydantic import BaseModel,field_serializer

class PriceHistoryResponse(BaseModel):
    id: int
    price: float
    recorded_at: datetime

    @field_serializer('recorded_at')
    def format_date(self, dt: datetime, _info):

        return dt.strftime("%d.%m.%Y %H:%M:%S")

    class Config:
        from_attributes = True