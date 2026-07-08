from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, status

from app.core.dependencies import SessionDep
from app.schemas.post import (
    PostCreateRequest,
    PostListResponse,
    PostResponse,
    PostUpdateRequest,
)
from app.services.post_service import PostService

router = APIRouter(tags=["Posts"])

SkipQuery = Annotated[int, Query(ge=0)]
LimitQuery = Annotated[int, Query(ge=1, le=100)]


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(payload: PostCreateRequest, db: SessionDep):
    service = PostService(db)
    return await service.create_post(payload)


@router.get("", response_model=PostListResponse)
async def list_posts(db: SessionDep, skip: SkipQuery = 0, limit: LimitQuery = 10):
    service = PostService(db)
    posts, total = await service.get_posts(skip=skip, limit=limit)
    return {"total": total, "items": posts}


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID, db: SessionDep):
    service = PostService(db)
    return await service.get_post(post_id)


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(post_id: UUID, payload: PostUpdateRequest, db: SessionDep):
    service = PostService(db)
    return await service.update_post(post_id, payload)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: UUID, db: SessionDep):
    service = PostService(db)
    await service.delete_post(post_id)
