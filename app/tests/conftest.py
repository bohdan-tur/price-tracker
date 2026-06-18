import pytest_asyncio

from httpx import AsyncClient, ASGITransport
from app.main import app
from app.backend.db import Base,get_session
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession


DATABASE_URL ="postgresql+asyncpg://postgres:postgres@db:5432/test_postgres"

test_engine = create_async_engine(DATABASE_URL,echo=False)

test_session = async_sessionmaker(engine = test_engine,class_=AsyncSession,expire_on_commit=False)



@pytest_asyncio.fixture(autouse = True)
async def prepare_db():
    async with  test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        yield

    async with test_engine.begin() as conn:

        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with test_session() as session:
        yield session



@pytest_asyncio.fixture

async def async_client(db_session):


     async def  override_get_session():
         yield db_session

     app.dependency_overrides[get_session] = override_get_session
     transport = ASGITransport(app=app)

     async with AsyncClient(transport=transport,base_url="http://test") as client:
         yield client

     app.dependency_overrides.clear()
