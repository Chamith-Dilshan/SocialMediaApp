from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings
from app.models.user import User
from app.schemas.token import TokenData

# --- Config ---
SECRET_KEY: str = settings.SECRET_KEY
ALGORITHM: str = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# --- Password hashing (pwdlib + Argon2) ---
# password_hash  = PasswordHash((Argon2Hasher(),))
password_hash = PasswordHash.recommended()

# Pre-hashed dummy used during timing-safe rejection when user is not found
DUMMY_HASH = password_hash.hash("dummypassword")

# --- OAuth2 scheme ---
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login"
)  # need to provide the path to the login endpoint


# --- Password helpers ---
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


# --- JWT helpers ---
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: Annotated[str, Depends(oauth2_scheme)]) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return TokenData(user_id=user_id)
    except InvalidTokenError:
        raise credentials_exception


async def authenticate_user(
    self,
    email: str,
    password: str,
) -> User | bool:
    user = await self.get_user_by_email(email)
    if not user:
        verify_password(password, settings.ALGORITHM)  # timing-safe rejection
        return False
    if not verify_password(password, user.password):
        return False
    return user
