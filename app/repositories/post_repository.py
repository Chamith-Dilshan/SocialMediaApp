from uuid import UUID

from sqlalchemy import exists
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import DatabaseException
from app.custom_types.post_types import PostWithLikeData
from app.models.post import Post
from app.models.post_like import PostLike


class PostRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, post: Post) -> Post:
        try:
            self.db.add(post)
            await self.db.commit()
            await self.db.refresh(post)
            return post

        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseException() from e

    async def get_by_id(self, post_id: UUID, user_id: UUID) -> PostWithLikeData | None:
        stmt = (
            select(
                Post,
                func.count(PostLike.user_id).label("like_count"),
                exists()
                .where(PostLike.post_id == post_id, PostLike.user_id == user_id)
                .label("is_liked"),
            )
            .outerjoin(PostLike, Post.id == PostLike.post_id)
            .options(
                selectinload(Post.author),
            )
            .where(Post.id == post_id)
            .group_by(Post.id)
        )

        result = await self.db.execute(stmt)
        row = result.one_or_none()

        if row is None:
            return None
        post, like_count, is_liked = row
        return {
            "post": post,
            "like_count": like_count,
            "is_liked": is_liked,
        }

    async def get_model_by_id(
        self,
        post_id: UUID,
    ) -> Post | None:

        stmt = select(Post).options(selectinload(Post.author)).where(Post.id == post_id)

        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    def _posts_query(self, viewer_id: UUID):
        return (
            select(
                Post,
                func.count(PostLike.user_id).label("like_count"),
                exists()
                .where(
                    PostLike.post_id == Post.id,
                    PostLike.user_id == viewer_id,
                )
                .label("is_liked"),
            )
            .outerjoin(
                PostLike,
                Post.id == PostLike.post_id,
            )
            .options(
                selectinload(Post.author),
            )
            .group_by(Post.id)
        )

    async def get_posts_by_author(
        self,
        author_id: UUID,
        viewer_id: UUID,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
    ) -> tuple[list[PostWithLikeData], int]:

        stmt = (
            self._posts_query(viewer_id)
            .where(Post.author_id == author_id)
            .order_by(Post.created_at.desc())
        )

        count_stmt = (
            select(func.count()).select_from(Post).where(Post.author_id == author_id)
        )

        if search:
            search_filter = Post.title.ilike(f"%{search}%")

            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        stmt = stmt.offset(skip).limit(limit)

        total = await self.db.scalar(count_stmt)

        result = await self.db.execute(stmt)

        rows = result.all()

        posts: list[PostWithLikeData] = []

        for post, like_count, is_liked in rows:
            posts.append(
                PostWithLikeData(
                    post=post,
                    like_count=like_count,
                    is_liked=is_liked,
                )
            )

        return posts, total or 0

    async def get_all_posts(
        self,
        viewer_id: UUID,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
    ) -> tuple[list[PostWithLikeData], int]:

        stmt = self._posts_query(viewer_id).order_by(Post.created_at.desc())

        count_stmt = select(func.count()).select_from(Post)

        if search:
            search_filter = Post.title.ilike(f"%{search}%")

            stmt = stmt.where(search_filter)
            count_stmt = count_stmt.where(search_filter)

        stmt = stmt.offset(skip).limit(limit)

        total = await self.db.scalar(count_stmt)

        result = await self.db.execute(stmt)

        rows = result.all()

        posts: list[PostWithLikeData] = []

        for post, like_count, is_liked in rows:
            posts.append(
                PostWithLikeData(
                    post=post,
                    like_count=like_count,
                    is_liked=is_liked,
                )
            )

        return posts, total or 0

    async def delete(self, post: Post) -> None:
        try:
            await self.db.delete(post)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseException() from e

    async def update(self, post: Post) -> Post:
        try:
            await self.db.commit()
            await self.db.refresh(post)
            return post
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise DatabaseException() from e
