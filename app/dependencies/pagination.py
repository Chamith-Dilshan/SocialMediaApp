from typing import Annotated

from fastapi import Query
from pydantic import BaseModel

SkipQuery = Annotated[int, Query(ge=0)]
LimitQuery = Annotated[int, Query(ge=1, le=100)]


class PaginationParams(BaseModel):
    skip: int
    limit: int


def pagination_params(
    skip: SkipQuery = 0,
    limit: LimitQuery = 10,
) -> PaginationParams:
    return PaginationParams(
        skip=skip,
        limit=limit,
    )
