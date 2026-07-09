from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.config import settings
from app.core.dependencies import SessionDep
from app.core.security import get_current_user_dep
from app.schemas.token import TokenData
from app.schemas.user import (
    UserCreateRequest,
    UserListResponse,
    UserResponse,
    UserUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter(
    tags=["Users"],
    prefix=f"{settings.API_V1_PREFIX}/users",
)

SkipQuery = Annotated[int, Query(ge=0)]
LimitQuery = Annotated[int, Query(ge=1, le=100)]

# Reusable alias
CurrentUser = Annotated[TokenData, Depends(get_current_user_dep)]


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    payload: UserCreateRequest,
    db: SessionDep,
    current_user: CurrentUser,
):
    service = UserService(db)

    return await service.create_user(payload)


@router.get(
    "",
    response_model=UserListResponse,
)
async def list_users(
    db: SessionDep,
    current_user: CurrentUser,
    skip: SkipQuery = 0,
    limit: LimitQuery = 10,
):
    service = UserService(db)

    users, total = await service.list_users(
        skip,
        limit,
    )

    return {
        "total": total,
        "items": users,
    }


@router.get(
    "/{user_id}",
    response_model=UserResponse,
)
async def get_user(user_id: UUID, db: SessionDep, current_user: CurrentUser):
    service = UserService(db)

    return await service.get_user(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID, payload: UserUpdateRequest, db: SessionDep, current_user: CurrentUser
):
    service = UserService(db)

    return await service.update_user(
        user_id,
        payload,
    )


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(user_id: UUID, db: SessionDep, current_user: CurrentUser):
    service = UserService(db)

    await service.delete_user(user_id)
