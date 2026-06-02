"""
RAG AI Agent — LangChain + pgvector 기반 자연어 질의응답
지원 Agent 타입:
  - INTEGRATED: 전체 공정 통합 질의
  - ORDER:      수주·견적 특화
  - PRODUCTION: 생산·품질 특화
  - EQUIPMENT:  설비·이상 특화
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Any

from app.config import settings


# ── RAG 파이프라인 ────────────────────────────────────────────────────────────

async def query_rag_agent(
    query_text: str,
    agent_type: str = "INTEGRATED",
    session_id: str | None = None,
    db_session=None,
) -> dict[str, Any]:
    """
    pgvector 유사도 검색 → LLM 답변 생성.
    OpenAI API 키 없으면 에코 응답 반환.
    """
    query_id = str(uuid.uuid4())
    retrieved: list[dict] = []

    if not settings.OPENAI_API_KEY:
        return _echo_response(query_id, query_text, agent_type, session_id)

    try:
        retrieved = await _vector_search(query_text, agent_type)
        answer = await _generate_answer(query_text, retrieved, agent_type)
    except Exception as e:
        answer = f"[AI 오류] {str(e)}"

    result = {
        "query_id": query_id,
        "agent_type": agent_type,
        "response": answer,
        "retrieved_sources": retrieved,
        "session_id": session_id,
        "queried_at": datetime.now(timezone.utc).isoformat(),
    }

    if db_session:
        await _save_query_history(db_session, query_id, query_text, result)

    return result


async def _vector_search(query: str, agent_type: str) -> list[dict]:
    """pgvector에서 관련 문서 검색"""
    from langchain_openai import OpenAIEmbeddings
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    query_vec = await embeddings.aembed_query(query)
    vec_str = "[" + ",".join(map(str, query_vec)) + "]"

    # pgvector 코사인 유사도 검색
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.connect() as conn:
        rows = await conn.execute(text("""
            SELECT content, source, 1 - (embedding <=> :vec::vector) AS similarity
            FROM knowledge_base
            WHERE agent_scope = :scope OR agent_scope = 'ALL'
            ORDER BY embedding <=> :vec::vector
            LIMIT 5
        """), {"vec": vec_str, "scope": agent_type})
        return [{"content": r[0], "source": r[1], "similarity": float(r[2])}
                for r in rows.fetchall()]


async def _generate_answer(query: str, contexts: list[dict], agent_type: str) -> str:
    """LLM으로 답변 생성"""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage

    context_text = "\n\n".join(
        f"[출처: {c['source']}]\n{c['content']}" for c in contexts
    ) if contexts else "관련 문서 없음"

    system_prompt = _get_system_prompt(agent_type)
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"컨텍스트:\n{context_text}\n\n질문: {query}"),
    ]
    response = await llm.ainvoke(messages)
    return response.content


def _get_system_prompt(agent_type: str) -> str:
    base = "당신은 부영기업 스마트공장 MES AI 어시스턴트입니다. 제조 공정 데이터를 기반으로 정확하고 간결하게 답변하세요."
    prompts = {
        "ORDER":      base + " 수주, 견적, BOM에 특화되어 있습니다.",
        "PRODUCTION": base + " 생산 LOT, 공정 실적, 불량 분석에 특화되어 있습니다.",
        "EQUIPMENT":  base + " 설비 상태, 센서 이상 감지, OEE 분석에 특화되어 있습니다.",
        "INTEGRATED": base + " 전체 공정(수주→생산→출하)을 통합 조회합니다.",
    }
    return prompts.get(agent_type, base)


def _echo_response(query_id: str, query: str, agent_type: str, session_id) -> dict:
    return {
        "query_id": query_id,
        "agent_type": agent_type,
        "response": f"[개발 모드 — OPENAI_API_KEY 미설정] 수신한 질의: '{query}'",
        "retrieved_sources": [],
        "session_id": session_id,
        "queried_at": datetime.now(timezone.utc).isoformat(),
    }


async def _save_query_history(db_session, query_id: str, query: str, result: dict):
    """ai_agent_query 테이블에 이력 저장"""
    from sqlalchemy import text
    try:
        await db_session.execute(text("""
            INSERT INTO ai_agent_query (query_id, agent_type, query_text, response_text, session_id, queried_at)
            VALUES (:qid, :atype, :query, :response, :session, :ts)
            ON CONFLICT DO NOTHING
        """), {
            "qid": query_id,
            "atype": result["agent_type"],
            "query": query,
            "response": result["response"],
            "session": result.get("session_id"),
            "ts": result["queried_at"],
        })
    except Exception:
        pass
