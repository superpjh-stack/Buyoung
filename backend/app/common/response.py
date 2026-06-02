from typing import Any, Optional
from pydantic import BaseModel


class Meta(BaseModel):
    page: int = 1
    limit: int = 20
    total: int = 0


class APIResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    meta: Optional[Meta] = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    detail: Optional[str] = None


class APIError(BaseModel):
    success: bool = False
    error: ErrorDetail


def ok(data: Any = None, meta: Optional[Meta] = None) -> APIResponse:
    return APIResponse(data=data, meta=meta)


def paginated(data: Any, page: int, limit: int, total: int) -> APIResponse:
    return APIResponse(data=data, meta=Meta(page=page, limit=limit, total=total))
