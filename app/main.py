import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers import auth, health, item, user
from app.core.config import settings
from app.core.logging import setup_logging

setup_logging()
logger = logging.getLogger("root")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application started successfully")

    yield

    logger.info("Application is shutting down")


app = FastAPI(title="Price Tracker", description="Price Tracker API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(item.router)
app.include_router(health.router)
