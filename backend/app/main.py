from fastapi import FastAPI

from app.api.router import api_router
from app.config import settings
from app.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(api_router)
