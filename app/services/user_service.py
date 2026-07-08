from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ConflictException,
    NotFoundException,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    UserCreateRequest,
    UserUpdateRequest,
)


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(
        self,
        payload: UserCreateRequest,
    ) -> User:

        existing_user = await self.repository.get_by_email(payload.email)

        if existing_user:
            raise ConflictException(
                message="Email already exists",
                status_code=409,
            )

        user = User(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )

        return await self.repository.create(user)

    async def get_user(
        self,
        user_id: UUID,
    ) -> User:

        user = await self.repository.get_by_id(user_id)

        if not user:
            raise NotFoundException(
                message="User not found",
                status_code=404,
            )

        return user

    async def list_users(
        self,
        skip: int,
        limit: int,
    ):
        return await self.repository.get_all(
            skip=skip,
            limit=limit,
        )

    async def update_user(
        self,
        user_id: UUID,
        payload: UserUpdateRequest,
    ) -> User:

        user = await self.get_user(user_id)

        if payload.first_name is not None:
            user.first_name = payload.first_name

        if payload.last_name is not None:
            user.last_name = payload.last_name

        if payload.password is not None:
            user.password = payload.password

        return await self.repository.update(user)

    async def delete_user(
        self,
        user_id: UUID,
    ) -> None:

        user = await self.get_user(user_id)

        await self.repository.delete(user)
