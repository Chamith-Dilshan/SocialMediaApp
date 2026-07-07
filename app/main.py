from fastapi import FastAPI

from app.api.v1 import users
from app.core.config import settings
from app.core.exception_handlers import (
    app_exception_handler,
)
from app.core.exceptions import AppException

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.add_exception_handler(
    AppException,
    app_exception_handler,
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_PREFIX}/users",
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }
