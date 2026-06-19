from celery import Celery
from datetime import UTC
from app.backend.db import AsyncSessionLocal
from sqlalchemy import select
from app.models.item import Item
import asyncio
from app.backend.scraper import get_current_price
from app.models.price_history import PriceHistory
from celery.schedules import crontab
from app.backend.dependencies import db_dependency


celery_app = Celery("price_tracker",
                    broker="redis://redis:6379/0",
                    backend="redis://redis:6379/0")


celery_app.conf.update(
                       task_serializer="json",
                       accept_content=["json"],
                       result_serializer="json",
                       timezone="UTC",
                       enable_utc=True,
                       broker_connection_retry_on_startup=True

                                                )


async def process_prices_async(db:db_dependency) -> dict:
    changes_count = 0
    try:
        result = await db.execute(select(Item))
        items = result.scalars().all()

        for item in items:
            new_price = await get_current_price(str(item.url))

            if new_price and new_price != item.current_price:
                new_price_history = PriceHistory(
                    item_id=item.id,
                    price=new_price
                )
                db.add(new_price_history)

                item.current_price = new_price
                changes_count += 1

        await db.commit()
        return {"status": "success", "updated_items": changes_count}

    except Exception as e:
        await db.rollback()
        return {"status": "error", "detail": str(e)}



@celery_app.task(name="update_item_prices")
def update_item_prices() -> dict:
    async def _run_task():
        async with AsyncSessionLocal() as db:
            return await process_prices_async(db)

    return asyncio.run(_run_task())




celery_app.conf.beat_schedule = {

    "update-prices-daily": {

        "task": "update_item_prices",
        "schedule": crontab(hour=3,minute=0)
    }
}
