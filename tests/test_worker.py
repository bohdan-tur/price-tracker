from unittest.mock import patch

from app.worker.worker import process_prices_async
from app.models.item import Item


async def test_process_price_async_success(create_test_user, db_session):

    user = await create_test_user()

    item = Item(
        title="Test item for worker",
        url="https://rozetka.com.ua/ua/test_item/",
        current_price=1000.0,
        user_id=user.id,
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)

    with patch("app.worker.worker.get_current_price", return_value=1200.0):
        result = await process_prices_async(db=db_session)

        assert result["status"] == "success"
        assert result["updated_items"] >= 1

        await db_session.refresh(item)
        assert item.current_price == 1200.0
