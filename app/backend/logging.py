import logging
import os
from logging.config import dictConfig
from pydantic import BaseModel

class LogConfig(BaseModel):
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
    }
    handlers: dict = {
        "default": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/app.log",
            "formatter": "default",
        },
    }
    loggers: dict = {
        "root": {"handlers": ["default", "file"], "level": "INFO"},
    }

def setup_logging():

    if not os.path.exists("logs"):
        os.makedirs("logs", exist_ok=True)

    dictConfig(LogConfig().model_dump())