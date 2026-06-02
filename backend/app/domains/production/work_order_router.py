from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID
from typing import Optional

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.common.response import ok, paginated
from app.common.pagination import PaginationParams, get_pagination
from app.common.exceptions import NotFoundError
from app.domains.production.models import WorkOrder
from app.domains.production.schemas import WorkOrderCreate, WorkOrderOut

router = APIRouter()

VALID_STATUS_TRANSITIONS = {
    "PLANNED": "IN_PROGRESS",
    "IN_PROGRESS": "COMPLETED",
}


class WorkOrderStatusUpdate(BaseModel):
    status: str


@router.get("")
async def list_work_orders(
    status: Optional[str] = None,
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    q = select(WorkOrder)
    if status:
        q = q.where(WorkOrder.status == status)
    total = await db.scalar(select(func.count()).select_from(q.subquery()))
    result = await db.execute(q.offset(pagination.offset).limit(pagination.limit))
    work_orders = result.scalars().all()
    return paginated([WorkOrderOut.model_validate(wo) for wo in work_orders],
                     pagination.page, pagination.limit, total)


@router.post("", status_code=201)
async def create_work_order(
    body: WorkOrderCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("ADMIN", "MANAGER")),
):
    from datetime import datetime
    work_order_no = f"WO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    work_order = WorkOrder(work_order_no=work_order_no, **body.model_dump())
    db.add(work_order)
    await db.flush()
    return ok(WorkOrderOut.model_validate(work_order))


@router.get("/{work_order_id}")
async def get_work_order(
    work_order_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    work_order = await db.get(WorkOrder, work_order_id)
    if not work_order:
        raise NotFoundError("작업지시를 찾을 수 없습니다.")
    return ok(WorkOrderOut.model_validate(work_order))


@router.put("/{work_order_id}/status")
async def update_work_order_status(
    work_order_id: UUID,
    body: WorkOrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("ADMIN", "MANAGER")),
):
    work_order = await db.get(WorkOrder, work_order_id)
    if not work_order:
        raise NotFoundError("작업지시를 찾을 수 없습니다.")
    allowed_next = VALID_STATUS_TRANSITIONS.get(work_order.status)
    if body.status != allowed_next:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=422,
            detail=f"'{work_order.status}' 상태에서 '{body.status}'으로 변경할 수 없습니다. "
                   f"허용된 다음 상태: {allowed_next}",
        )
    work_order.status = body.status
    await db.flush()
    return ok(WorkOrderOut.model_validate(work_order))
