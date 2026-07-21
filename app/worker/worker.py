import asyncio
import logging

from celery import Celery
from celery.schedules import crontab
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import AsyncSessionLocal
from app.models.item import Item
from app.models.price_history import PriceHistory
from app.services.scraper import get_current_price

logger = logging.getLogger("root")

celery_app = Celery(
    "price_tracker", broker="redis://redis:6379/0", backend="redis://redis:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)


async def process_prices_async(db: AsyncSession) -> dict:
    changes_count = 0
    logger.info("Started processing prices update task.")

    try:
        result = await db.execute(select(Item))
        items = result.scalars().all()

        for item in items:
            new_price = await get_current_price(str(item.url))
            if new_price and new_price != item.current_price:
                logger.info(
                    f"Price updated for item {item.id}:"
                    f" {item.current_price} -> {new_price}"
                )
                new_price_history = PriceHistory(item_id=item.id, price=new_price)
                db.add(new_price_history)
                item.current_price = new_price
                changes_count += 1

        if changes_count > 0:
            await db.commit()

        logger.info(f"Price update task completed. Items updated: {changes_count}")
        return {"status": "success", "updated_items": changes_count}

    except Exception as e:
        await db.rollback()
        logger.error(f"Error during price processing: {str(e)}")
        raise e


@celery_app.task(
    name="update_item_prices",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=3600,
    max_retries=5,
)
def update_item_prices(self) -> dict:
    async def _run_task():
        async with AsyncSessionLocal() as db:
            return await process_prices_async(db)

    return asyncio.run(_run_task())


celery_app.conf.beat_schedule = {
    "update-prices-daily": {
        "task": "update_item_prices",
        "schedule": crontab(hour=3, minute=0),
    }
}
