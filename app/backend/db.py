from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.backend.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)


AsyncSessionLocal = async_sessionmaker(bind=engine, autoflush=False, autocommit=False)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session


class Base(DeclarativeBase):
    pass
