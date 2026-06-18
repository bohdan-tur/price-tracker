from conftest import async_client
from httpx import AsyncClient
from app.models.item import Item
from app.backend.dependencies import get_current_user
from app.main import app

from sqlalchemy import select
from conftest import db_session
async def test_create_item(async_client:AsyncClient,create_test_user):

    user =  await create_test_user()

    app.dependency_overrides[get_current_user] = lambda: user

    payload = {
        "title":"Test title",
         "url": "https://fake-site-example.com/product/123"
    }

    response = await async_client.post("/items/",json=payload)

    assert response.status_code == 201




async def test_get_items(async_client:AsyncClient,create_test_user):
    user = await create_test_user()

    app.dependency_overrides[get_current_user] = lambda: user

    response = await async_client.get("/items/")

    assert response.status_code == 200
    assert len(response.json()) == 0



async def test_delete_item(async_client:AsyncClient,create_test_user,db_session):

    user = await create_test_user()

    app.dependency_overrides[get_current_user] = lambda: user

    item = Item(
        title="Test title",
        url="https://fake-site-example.com/product/123",
        current_price = None,
        user_id = user.id,
        owner = user,
        price_histories = [],

    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)

    response = await async_client.delete(f"/items/{item.id}")

    assert response.status_code == 204

    query = await db_session.execute(select(Item).where(Item.id == item.id))
    deleted_item = query.scalar_one_or_none()
    assert deleted_item is None

    app.dependency_overrides.pop(get_current_user)




