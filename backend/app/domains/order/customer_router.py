from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.database import get_db
from app.auth.dependencies import get_current_user, require_role
from app.common.response import ok, paginated
from app.common.pagination import PaginationParams, get_pagination
from app.common.exceptions import NotFoundError
from app.domains.order.models import Customer
from app.domains.order.schemas import CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter()


@router.get("")
async def list_customers(
    pagination: PaginationParams = Depends(get_pagination),
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    total = await db.scalar(select(func.count()).where(Customer.is_deleted == False))
    result = await db.execute(
        select(Customer).where(Customer.is_deleted == False)
        .offset(pagination.offset).limit(pagination.limit)
    )
    customers = result.scalars().all()
    return paginated([CustomerOut.model_validate(c) for c in customers],
                     pagination.page, pagination.limit, total)


@router.post("", status_code=201)
async def create_customer(
    body: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("ADMIN", "MANAGER")),
):
    customer = Customer(**body.model_dump())
    db.add(customer)
    await db.flush()
    return ok(CustomerOut.model_validate(customer))


@router.get("/{customer_id}")
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(get_current_user),
):
    customer = await db.get(Customer, customer_id)
    if not customer or customer.is_deleted:
        raise NotFoundError("고객사를 찾을 수 없습니다.")
    return ok(CustomerOut.model_validate(customer))


@router.put("/{customer_id}")
async def update_customer(
    customer_id: UUID,
    body: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("ADMIN", "MANAGER")),
):
    customer = await db.get(Customer, customer_id)
    if not customer or customer.is_deleted:
        raise NotFoundError("고객사를 찾을 수 없습니다.")
    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(customer, field, value)
    await db.flush()
    return ok(CustomerOut.model_validate(customer))


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    _=Depends(require_role("ADMIN", "MANAGER")),
):
    customer = await db.get(Customer, customer_id)
    if not customer or customer.is_deleted:
        raise NotFoundError("고객사를 찾을 수 없습니다.")
    customer.is_deleted = True
    await db.flush()
