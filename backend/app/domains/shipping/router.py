from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.common.response import ok, paginated
from app.common.pagination import PaginationParams, get_pagination
from app.common.exceptions import NotFoundError
from app.domains.shipping.models import ShippingOrder, ShippingLot, Claim
from app.domains.shipping.schemas import (
    ShippingOrderCreate, ShippingOrderOut,
    ShippingLotCreate, ShippingLotOut,
    ClaimCreate, ClaimOut,
)


class TrackingUpdate(BaseModel):
    tracking_no: str


class ClaimResolveBody(BaseModel):
    root_cause: str

router = APIRouter()


@router.get("")
async def list_shipping_orders(
    status: str | None = None,
    risk: bool | None = None,
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(ShippingOrder)
    if status:
        q = q.where(ShippingOrder.shipping_status == status)
    if risk is not None:
        q = q.where(ShippingOrder.delivery_risk_flag == risk)
    total = await db.scalar(select(func.count()).select_from(q.subquery()))
    result = await db.execute(q.offset(pagination.offset).limit(pagination.limit))
    orders = result.scalars().all()
    return paginated([ShippingOrderOut.model_validate(o) for o in orders],
                     pagination.page, pagination.limit, total)


@router.post("", status_code=201)
async def create_shipping_order(
    body: ShippingOrderCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    so = ShippingOrder(
        shipping_order_no=f"SHP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        **body.model_dump(),
    )
    db.add(so)
    await db.flush()
    return ok(ShippingOrderOut.model_validate(so))


@router.get("/delivery-risk")
async def delivery_risk_orders(db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(ShippingOrder).where(ShippingOrder.delivery_risk_flag == True))
    return ok([ShippingOrderOut.model_validate(o) for o in result.scalars()])


@router.get("/{shipping_order_id}")
async def get_shipping_order(shipping_order_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    so = await db.get(ShippingOrder, shipping_order_id)
    if not so:
        raise NotFoundError("출하 지시를 찾을 수 없습니다.")
    return ok(ShippingOrderOut.model_validate(so))


@router.post("/{shipping_order_id}/lots", status_code=201)
async def add_shipping_lot(
    shipping_order_id: UUID,
    body: ShippingLotCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    lot = ShippingLot(shipping_order_id=shipping_order_id, **body.model_dump())
    db.add(lot)
    await db.flush()
    return ok(ShippingLotOut.model_validate(lot))


# ── Claims ────────────────────────────────────────────────────────────────────

@router.post("/claims", status_code=201)
async def create_claim(
    body: ClaimCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    claim = Claim(
        claim_no=f"CLM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        claim_date=date.today(),
        **body.model_dump(),
    )
    db.add(claim)
    await db.flush()
    return ok(ClaimOut.model_validate(claim))


@router.get("/claims/{claim_id}")
async def get_claim(claim_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    claim = await db.get(Claim, claim_id)
    if not claim:
        raise NotFoundError("클레임을 찾을 수 없습니다.")
    return ok(ClaimOut.model_validate(claim))


# ── Additional Shipping Order endpoints ───────────────────────────────────────

@router.put("/{shipping_order_id}/ship")
async def ship_order(
    shipping_order_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    so = await db.get(ShippingOrder, shipping_order_id)
    if not so:
        raise NotFoundError("출하 지시를 찾을 수 없습니다.")
    so.shipping_status = "SHIPPED"
    await db.flush()
    return ok(ShippingOrderOut.model_validate(so))


@router.get("/{shipping_order_id}/lots")
async def list_shipping_lots(
    shipping_order_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    so = await db.get(ShippingOrder, shipping_order_id)
    if not so:
        raise NotFoundError("출하 지시를 찾을 수 없습니다.")
    result = await db.execute(
        select(ShippingLot).where(ShippingLot.shipping_order_id == shipping_order_id)
    )
    lots = result.scalars().all()
    return ok([ShippingLotOut.model_validate(lot) for lot in lots])


# ── Shipping Lot endpoints ─────────────────────────────────────────────────────

@router.put("/shipping-lots/{shipping_lot_id}/tracking")
async def update_tracking(
    shipping_lot_id: UUID,
    body: TrackingUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    lot = await db.get(ShippingLot, shipping_lot_id)
    if not lot:
        raise NotFoundError("출하 LOT를 찾을 수 없습니다.")
    lot.tracking_no = body.tracking_no
    await db.flush()
    return ok(ShippingLotOut.model_validate(lot))


# ── Additional Claim endpoints ─────────────────────────────────────────────────

@router.get("/claims")
async def list_claims(
    status: Optional[str] = None,
    customer_id: Optional[UUID] = None,
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(Claim)
    if status:
        q = q.where(Claim.status == status)
    if customer_id:
        q = q.where(Claim.customer_id == customer_id)
    total = await db.scalar(select(func.count()).select_from(q.subquery()))
    result = await db.execute(q.offset(pagination.offset).limit(pagination.limit))
    claims = result.scalars().all()
    return paginated(
        [ClaimOut.model_validate(c) for c in claims],
        pagination.page, pagination.limit, total,
    )


@router.put("/claims/{claim_id}/investigate")
async def investigate_claim(
    claim_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    claim = await db.get(Claim, claim_id)
    if not claim:
        raise NotFoundError("클레임을 찾을 수 없습니다.")
    claim.status = "INVESTIGATING"
    await db.flush()
    return ok(ClaimOut.model_validate(claim))


@router.put("/claims/{claim_id}/resolve")
async def resolve_claim(
    claim_id: UUID,
    body: ClaimResolveBody,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    claim = await db.get(Claim, claim_id)
    if not claim:
        raise NotFoundError("클레임을 찾을 수 없습니다.")
    claim.status = "RESOLVED"
    claim.root_cause = body.root_cause
    await db.flush()
    return ok(ClaimOut.model_validate(claim))
