from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field


class PaginationParams(BaseModel):
    limit: int = Field(
        default=10, ge=1, le=100, description="Number of items to return"
    )
    offset: int = Field(default=0, ge=0, description="Number of items to skip")

    model_config = ConfigDict(from_attributes=True)


def get_pagination(
    limit: Annotated[
        int, Query(ge=1, le=100, description="Number of items to return")
    ] = 10,
    offset: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)
