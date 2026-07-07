from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse[T](BaseModel):
    success: bool = True
    message: str
    data: T | None = None


class PaginatedResponse[T](BaseModel):
    success: bool = True
    message: str
    total: int
    items: list[T]
