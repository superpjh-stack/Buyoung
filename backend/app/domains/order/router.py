from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.common.response import ok, paginated
from app.common.pagination import PaginationParams, get_pagination
from app.common.exceptions import NotFoundError
from app.domains.order.models import Order, Quote, BOM
from app.domains.order.schemas import OrderCreate, OrderOut, QuoteTrigger, QuoteOut

router = APIRouter()


# ── Order ─────────────────────────────────────────────────────────────────────

@router.get("")
async def list_orders(
    status: str | None = None,
    customer_id: UUID | None = None,
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(Order).where(Order.is_deleted == False)
    if status:
        q = q.where(Order.status == status)
    if customer_id:
        q = q.where(Order.customer_id == customer_id)
    total = await db.scalar(select(func.count()).select_from(q.subquery()))
    result = await db.execute(q.offset(pagination.offset).limit(pagination.limit))
    orders = result.scalars().all()
    return paginated([OrderOut.model_validate(o) for o in orders],
                     pagination.page, pagination.limit, total)


@router.post("", status_code=201)
async def create_order(
    body: OrderCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    from datetime import datetime
    order_no = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    order = Order(order_no=order_no, **body.model_dump())
    db.add(order)
    await db.flush()
    return ok(OrderOut.model_validate(order))


@router.get("/{order_id}")
async def get_order(order_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    order = await db.get(Order, order_id)
    if not order or order.is_deleted:
        raise NotFoundError("수주를 찾을 수 없습니다.")
    return ok(OrderOut.model_validate(order))


@router.get("/{order_id}/traceability")
async def get_traceability(order_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    """수주 전체 Digital Thread 조회"""
    order = await db.get(Order, order_id)
    if not order or order.is_deleted:
        raise NotFoundError("수주를 찾을 수 없습니다.")
    # TODO: 생산LOT, 검사, 출하 데이터 조인 조회
    return ok({"order_id": str(order_id), "order_no": order.order_no, "status": order.status})


# ── Quote ─────────────────────────────────────────────────────────────────────

@router.post("/{order_id}/quotes", status_code=201)
async def trigger_quote(
    order_id: UUID,
    body: QuoteTrigger,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    """CAD AI 기반 견적 자동 산출"""
    from datetime import datetime
    quote_no = f"QTE-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    quote = Quote(order_id=order_id, quote_no=quote_no, status="AUTO")
    db.add(quote)
    await db.flush()
    # TODO: background_tasks.add_task(run_cad_quote_ai, quote.quote_id, body.drawing_id)
    return ok(QuoteOut.model_validate(quote))


@router.get("/{order_id}/quotes")
async def list_quotes(order_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(Quote).where(Quote.order_id == order_id))
    quotes = result.scalars().all()
    return ok([QuoteOut.model_validate(q) for q in quotes])


# ── BOM ───────────────────────────────────────────────────────────────────────

@router.post("/{order_id}/bom/generate", status_code=201)
async def generate_bom(order_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    """GNN 기반 BOM 자동 생성"""
    bom = BOM(order_id=order_id, bom_version="v1", status="DRAFT")
    db.add(bom)
    await db.flush()
    # TODO: AI BOM 생성 로직
    return ok({"bom_id": str(bom.bom_id), "status": bom.status})


@router.get("/{order_id}/bom")
async def get_bom(order_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    result = await db.execute(select(BOM).where(BOM.order_id == order_id))
    bom = result.scalar_one_or_none()
    if not bom:
        raise NotFoundError("BOM이 없습니다.")
    return ok({"bom_id": str(bom.bom_id), "bom_version": bom.bom_version, "status": bom.status})
