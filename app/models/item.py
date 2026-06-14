from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.backend.db import Base

class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    url: Mapped[str]
    current_price: Mapped[float | None] = mapped_column(default=None)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")
    price_histories = relationship("PriceHistory", back_populates="item")