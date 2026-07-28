from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import auth, posts, users, likes
from app.core.config import settings
from app.core.db_init import create_tables
from app.core.exceptions import AppException


@asynccontextmanager
async def lifespan(application: FastAPI):
    await create_tables()
    yield


app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)


# ---------------------------------------------------------------------------
# Global handler for all domain exceptions (NotFoundException → 404, etc.)
# ---------------------------------------------------------------------------
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


app.include_router(
    auth.router,
)

app.include_router(
    users.router,
)

app.include_router(
    posts.router,
)

app.include_router(
    likes.router,
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
    }
