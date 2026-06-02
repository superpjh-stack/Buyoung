from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.common.exceptions import register_exception_handlers
from app.auth.router import router as auth_router
from app.domains.order.router import router as order_router
from app.domains.order.customer_router import router as customer_router
from app.domains.order.quote_router import router as quote_router
from app.domains.cad.router import router as cad_router
from app.domains.receiving.router import router as receiving_router
from app.domains.receiving.supplier_router import router as supplier_router
from app.domains.receiving.material_router import router as material_router
from app.domains.receiving.inventory_router import router as inventory_router
from app.domains.production.router import router as production_router
from app.domains.production.work_order_router import router as work_order_router
from app.domains.quality.router import router as quality_router
from app.domains.shipping.router import router as shipping_router
from app.domains.equipment.router import router as equipment_router
from app.domains.ai.router import router as ai_router
from app.websocket.router import router as ws_router

app = FastAPI(
    title="Buyoung AI MES API",
    version="1.0.0",
    description="부영기업 제조AI 스마트공장 MES REST API",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

PREFIX = "/v1"

app.include_router(auth_router,         prefix=f"{PREFIX}/auth",             tags=["Auth"])
app.include_router(customer_router,     prefix=f"{PREFIX}/customers",        tags=["Customer"])
app.include_router(order_router,        prefix=f"{PREFIX}/orders",           tags=["Order"])
app.include_router(quote_router,        prefix=f"{PREFIX}/quotes",           tags=["Quote"])
app.include_router(cad_router,          prefix=f"{PREFIX}/cad-drawings",     tags=["CAD"])
app.include_router(receiving_router,    prefix=f"{PREFIX}/receiving-lots",   tags=["Receiving"])
app.include_router(supplier_router,     prefix=f"{PREFIX}/suppliers",         tags=["Supplier"])
app.include_router(material_router,     prefix=f"{PREFIX}/materials",         tags=["Material"])
app.include_router(inventory_router,    prefix=f"{PREFIX}/inventory",         tags=["Inventory"])
app.include_router(work_order_router,   prefix=f"{PREFIX}/work-orders",      tags=["WorkOrder"])
app.include_router(production_router,   prefix=f"{PREFIX}/production-lots",  tags=["Production"])
app.include_router(quality_router,    prefix=f"{PREFIX}/quality-inspections", tags=["Quality"])
app.include_router(shipping_router,   prefix=f"{PREFIX}/shipping-orders", tags=["Shipping"])
app.include_router(equipment_router,  prefix=f"{PREFIX}/equipment",  tags=["Equipment"])
app.include_router(ai_router,         prefix=f"{PREFIX}/ai",         tags=["AI"])
app.include_router(ws_router,         prefix="/ws",                  tags=["WebSocket"])


@app.get("/health", tags=["System"])
async def health():
    return {"status": "ok", "version": "1.0.0"}
