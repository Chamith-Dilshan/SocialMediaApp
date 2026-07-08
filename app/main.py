from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import posts, users
from app.core.config import settings
from app.core.db_init import create_tables
from app.core.exception_handlers import (
    app_exception_handler,
)
from app.core.exceptions import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)

# app.add_exception_handler(
#     AppException,
#     app_exception_handler,
# )

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_PREFIX}/users",
)
app.include_router(
    posts.router,
    prefix=f"{settings.API_V1_PREFIX}/posts",
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }
