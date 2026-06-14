from pydantic import DeclarativeBase
from config import settings
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession

engine = create_async_engine(settings.DATABASE_URL,echo=True)


AsyncSessionLocal = async_sessionmaker(bind=engine,autoflush=False,autocommit=False)


async def get_session():
    async with AsyncSessionLocal() as session:
        yield session



class Base(DeclarativeBase):
    pass