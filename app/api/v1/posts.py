from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.config import settings
from app.dependancies.database_dep import SessionDep
from app.dependancies.security_dep import get_current_user_dep
from app.schemas.post import (
    PostCreateRequest,
    PostListResponse,
    PostResponse,
    PostUpdateRequest,
)
from app.schemas.token import TokenData
from app.services.post_service import PostService

router = APIRouter(
    tags=["Posts"],
    prefix=f"{settings.API_V1_PREFIX}/posts",
)

SkipQuery = Annotated[int, Query(ge=0)]
LimitQuery = Annotated[int, Query(ge=1, le=100)]

# Reusable alias
CurrentUser = Annotated[TokenData, Depends(get_current_user_dep)]


@router.post(
    "",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    payload: PostCreateRequest, db: SessionDep, current_user: CurrentUser
):
    service = PostService(db)
    return await service.create_post(payload, current_user.id)


@router.get("", response_model=PostListResponse)
async def list_posts(
    db: SessionDep,
    current_user: CurrentUser,
    search: str | None = None,
    skip: SkipQuery = 0,
    limit: LimitQuery = 10,
):
    service = PostService(db)
    posts, total = await service.get_posts(search=search, skip=skip, limit=limit)
    return {"total": total, "items": posts}


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID, db: SessionDep, current_user: CurrentUser):
    service = PostService(db)
    return await service.get_post(post_id, current_user.id)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: UUID, payload: PostUpdateRequest, db: SessionDep, current_user: CurrentUser
):
    service = PostService(db)
    return await service.update_post(post_id, payload, current_user.id)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: UUID, db: SessionDep, current_user: CurrentUser):
    service = PostService(db)
    await service.delete_post(post_id, current_user.id)
