from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status

from app.core.security import (
    decode_token,
    oauth2_scheme,
)
from app.dependancies.database_dep import SessionDep
from app.schemas.user import UserResponse
from app.services.user_service import UserService


# --- Dependency: get current user (injected into protected routes) ---
async def get_current_user_dep(
    token: Annotated[str, Depends(oauth2_scheme)], db: SessionDep
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    service = UserService(db)
    token_data = decode_token(token)
    user = await service.get_user(UUID(token_data.user_id))
    if user is None:
        raise credentials_exception
    return user
