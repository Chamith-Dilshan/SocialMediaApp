from app.core.base import Base
from app.core.database import engine
from app.models.post import Post
from app.models.user import User


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
