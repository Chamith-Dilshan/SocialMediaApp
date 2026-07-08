from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PostCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1)
    published: bool = Field(default=True)
    author_id: UUID


class PostUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    published: bool | None = None


class PostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    author_id: UUID
    title: str
    content: str
    published: bool
    created_at: datetime
    updated_at: datetime


class PostListResponse(BaseModel):
    total: int
    items: list[PostResponse]
