from fastapi import FastAPI
from app.routers import auth
from app.routers import user
from app.routers import item
from app.backend.logging import setup_logging
from contextlib import asynccontextmanager
import logging

setup_logging()
logger = logging.getLogger("root")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started successfully")

    yield

    logger.info("Application is shutting down")


app = FastAPI(title="Price Tracker", description="Price Tracker API",lifespan=lifespan)



app.include_router(auth.router)
app.include_router(user.router)
app.include_router(item.router)



