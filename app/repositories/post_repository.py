from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.post import Post


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, post: Post) -> Post:
        self.db.add(post)
        await self.db.commit()
        await self.db.refresh(post)
        return post

    async def get_by_id(self, post_id: UUID) -> Post | None:
        stmt = select(Post).where(Post.id == post_id).limit(1)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self, skip: int = 0, limit: int = 10, search: str | None = None
    ) -> tuple[list[Post], int]:
        count_stmt = select(func.count()).select_from(Post)
        stmt = (
            select(Post)
            .filter(Post.title.contains(search))
            .offset(skip)
            .limit(limit)
            .order_by(Post.created_at.desc())
        )

        total = await self.db.scalar(count_stmt)
        result = await self.db.execute(stmt)
        posts = list(result.scalars().all())
        return posts, total or 0

    async def delete(self, post: Post) -> None:
        await self.db.delete(post)
        await self.db.commit()

    async def update(self, post: Post) -> Post:
        await self.db.commit()
        await self.db.refresh(post)
        return post
