from uuid import UUID

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import DatabaseException, NotFoundException
from app.models.post import Post
from app.repositories.post_repository import PostRepository
from app.schemas.post import PostCreateRequest, PostUpdateRequest


class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.post_repository = PostRepository(db)

    async def create_post(self, data: PostCreateRequest) -> Post:
        try:
            post = Post(
                title=data.title,
                content=data.content,
                published=data.published,
                user_id=data.user_id,
            )
            return await self.post_repository.create(post)
        except SQLAlchemyError as exc:
            await self.db.rollback()
            raise DatabaseException() from exc

    async def get_post(self, post_id: UUID) -> Post:
        post = await self.post_repository.get_by_id(post_id)

        if not post:
            raise NotFoundException(message="Post not found", status_code=404)

        return post

    async def get_posts(self, skip: int = 0, limit: int = 10) -> tuple[list[Post], int]:
        return await self.post_repository.get_all(skip=skip, limit=limit)

    async def update_post(self, post_id: UUID, data: PostUpdateRequest) -> Post:
        try:
            post = await self.get_post(post_id)
            update_data = data.model_dump(exclude_unset=True)

            for field, value in update_data.items():
                setattr(post, field, value)

            return await self.post_repository.update(post)
        except SQLAlchemyError as exc:
            await self.db.rollback()
            raise DatabaseException() from exc

    async def delete_post(self, post_id: UUID) -> None:
        try:
            post = await self.get_post(post_id)
            await self.post_repository.delete(post)
        except SQLAlchemyError as exc:
            await self.db.rollback()
            raise DatabaseException() from exc
