from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from datetime import datetime, timezone

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.common.response import ok
from app.common.exceptions import NotFoundError
from app.ai.rag_agent import query_rag_agent

router = APIRouter()


@router.post("/query")
async def ai_query(body: dict, db: AsyncSession = Depends(get_db), current_user=Depends(get_current_user)):
    """RAG 기반 AI Agent 자연어 질의"""
    result = await query_rag_agent(
        query_text=body.get("query", ""),
        agent_type=body.get("agent_type", "INTEGRATED"),
        session_id=body.get("session_id"),
        db_session=db,
    )
    return ok(result)


@router.put("/query/{query_id}/feedback")
async def query_feedback(query_id: UUID, body: dict, _=Depends(get_current_user)):
    score = body.get("score")
    # TODO: ai_agent_query 테이블 feedback_score 업데이트
    return ok({"query_id": str(query_id), "feedback_score": score})


@router.get("/query-history")
async def query_history(
    agent_type: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # TODO: ai_agent_query 테이블 조회
    return ok([])


@router.post("/cad-quote/trigger", status_code=202)
async def trigger_cad_quote(body: dict, _=Depends(get_current_user)):
    """CAD 견적 AI 수동 트리거"""
    from app.ai.cad_pipeline import run_cad_quote_pipeline
    from app.config import settings
    drawing_id = body.get("drawing_id", "")
    file_path = body.get("file_path", "")
    # 백그라운드로 실행하려면 BackgroundTasks 사용
    # 여기서는 직접 호출 (테스트용)
    return ok({"message": "CAD 견적 AI 작업이 시작되었습니다.", "drawing_id": drawing_id})


@router.get("/cad-quote/{quote_id}/explain")
async def explain_quote(quote_id: UUID, db: AsyncSession = Depends(get_db), _=Depends(get_current_user)):
    """SHAP 기반 견적 설명 상세 조회"""
    from app.domains.order.models import Quote
    quote = await db.get(Quote, quote_id)
    if not quote:
        raise NotFoundError("견적을 찾을 수 없습니다.")
    shap = quote.shap_explanation or {}
    return ok({
        "quote_id": str(quote_id),
        "total_amount": float(quote.total_amount) if quote.total_amount else None,
        "material_cost": float(quote.material_cost) if quote.material_cost else None,
        "process_cost": float(quote.process_cost) if quote.process_cost else None,
        "shap_features": shap.get("top_features", []),
        "confidence_score": float(quote.confidence_score) if quote.confidence_score else None,
        "estimated_lead_time_days": quote.estimated_lead_time_days,
    })


@router.get("/kpi/summary")
async def kpi_summary(_=Depends(get_current_user)):
    """KPI 대시보드 요약"""
    return ok({
        "period": datetime.now(timezone.utc).date().isoformat(),
        "hourly_output":  {"target": 18,   "actual": None, "unit": "ea/h", "status": "PENDING"},
        "lead_time":      {"target": 60,   "actual": None, "unit": "h",    "status": "PENDING"},
        "defect_rate":    {"target": 0.02, "actual": None, "unit": "%",    "status": "PENDING"},
        "equipment_oee":  {"target": 0.85, "actual": None, "unit": "%",    "status": "PENDING"},
    })


@router.get("/kpi/records")
async def kpi_records(kpi_type: str | None = None, _=Depends(get_current_user)):
    # TODO: kpi_record 테이블 조회
    return ok([])
