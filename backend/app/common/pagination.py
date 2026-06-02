from fastapi import Query
from dataclasses import dataclass


@dataclass
class PaginationParams:
    page: int
    limit: int
    sort: str
    order: str

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


def get_pagination(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    sort: str = Query(default="created_at"),
    order: str = Query(default="desc", pattern="^(asc|desc)$"),
) -> PaginationParams:
    return PaginationParams(page=page, limit=limit, sort=sort, order=order)
