from datetime import datetime
from pydantic import BaseModel, field_serializer, ConfigDict

class PriceHistoryResponse(BaseModel):
    id: int
    price: float
    recorded_at: datetime

    @field_serializer('recorded_at')
    def format_date(self, dt: datetime, _info):

        return dt.strftime("%d.%m.%Y %H:%M:%S")

    model_config = ConfigDict(from_attributes=True)