from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.common.response import ok
from app.common.exceptions import NotFoundError
from app.domains.order.models import Quote, Order
from app.domains.order.schemas import QuoteOut

router = APIRouter()


class QuoteRejectBody(BaseModel):
    reason: Optional[str] = None


@router.get("/{quote_id}")
async def get_quote(
    quote_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    quote = await db.get(Quote, quote_id)
    if not quote:
        raise NotFoundError("견적을 찾을 수 없습니다.")
    return ok(QuoteOut.model_validate(quote))


@router.put("/{quote_id}/approve")
async def approve_quote(
    quote_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("ADMIN", "MANAGER")),
):
    quote = await db.get(Quote, quote_id)
    if not quote:
        raise NotFoundError("견적을 찾을 수 없습니다.")
    quote.status = "APPROVED"
    order = await db.get(Order, quote.order_id)
    if order:
        order.status = "CONFIRMED"
    await db.flush()
    return ok(QuoteOut.model_validate(quote))


@router.put("/{quote_id}/reject")
async def reject_quote(
    quote_id: UUID,
    body: QuoteRejectBody,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("ADMIN", "MANAGER")),
):
    quote = await db.get(Quote, quote_id)
    if not quote:
        raise NotFoundError("견적을 찾을 수 없습니다.")
    quote.status = "REJECTED"
    order = await db.get(Order, quote.order_id)
    if order:
        order.status = "RECEIVED"
    await db.flush()
    return ok(QuoteOut.model_validate(quote))
