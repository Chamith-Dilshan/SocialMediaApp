from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.dtos.post_dto import PostCreateRequest, PostUpdateRequest
from app.dtos.post_dto import PostResponse
from app.mappers.post_mapper import post_to_response
from app.models.post import Post
from app.repositories.post_repository import PostRepository


class PostService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.post_repository = PostRepository(db)

    async def create_post(self, data: PostCreateRequest, user_id: UUID) -> Post:
        post = Post(
            title=data.title,
            content=data.content,
            published=data.published,
            author_id=user_id,
        )
        return await self.post_repository.create(post)

    async def get_post(
        self,
        post_id: UUID,
        user_id: UUID,
    ) -> PostResponse:
        post = await self.post_repository.get_by_id(post_id, user_id)

        if post is None:
            raise NotFoundException(
                message="Post not found", status_code=status.HTTP_404_NOT_FOUND
            )

        return post_to_response(post)

    def verify_post_owner(
        self,
        post: Post,
        user_id: UUID,
    ) -> None:

        if post.author_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not the author of this post",
            )

    async def get_posts_by_author(
        self,
        author_id: UUID,
        viewer_id: UUID,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
    ) -> tuple[list[PostResponse], int]:

        posts, total = await self.post_repository.get_posts_by_author(
            author_id=author_id,
            viewer_id=viewer_id,
            skip=skip,
            limit=limit,
            search=search,
        )
        return [post_to_response(post) for post in posts], total

    async def get_all_posts(
        self,
        viewer_id: UUID,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
    ) -> tuple[list[PostResponse], int]:

        posts, total = await self.post_repository.get_all_posts(
            viewer_id=viewer_id,
            skip=skip,
            limit=limit,
            search=search,
        )
        return [post_to_response(post) for post in posts], total

    async def update_post(
        self, post_id: UUID, data: PostUpdateRequest, user_id: UUID
    ) -> Post:
        post = await self.post_repository.get_model_by_id(post_id)
        if post is None:
            raise NotFoundException(
                message="Post not found", status_code=status.HTTP_404_NOT_FOUND
            )
        self.verify_post_owner(post, user_id)
        update_data = data.model_dump(
            exclude_unset=True
        )  # this makes sure only the fields that are set are updated

        for field, value in update_data.items():
            setattr(post, field, value)

        return await self.post_repository.update(post)

    async def delete_post(self, post_id: UUID, user_id: UUID) -> None:
        post = await self.post_repository.get_model_by_id(post_id)
        if post is None:
            raise NotFoundException(
                message="Post not found", status_code=status.HTTP_404_NOT_FOUND
            )
        self.verify_post_owner(post, user_id)
        await self.post_repository.delete(post)
