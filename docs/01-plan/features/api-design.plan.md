# [Plan] API Design — 부영기업 AI MES

## Feature Overview

부영기업 제조AI MES 시스템의 REST API 전체 설계.
erd.md(35개 테이블, 9개 도메인)를 기반으로 프론트엔드(Web Dashboard, POP, 스마트패드)와
AI 서브시스템(CAD 견적 AI, RAG Agent, ML Engine)이 사용하는 API 엔드포인트를 정의한다.

## Reference Documents

- `docs/intro.md` — 프로젝트 소개 및 목표
- `docs/problem.md` — AS-IS 문제 분석
- `docs/spec.md` — 시스템 명세 (아키텍처, 모듈, 클라우드 인프라)
- `docs/erd.md` — DB 설계 (35개 테이블, 9개 도메인)

## Scope

| 도메인 | 주요 API |
|--------|---------|
| 수주·견적 | 수주 CRUD, CAD 도면 업로드·파싱, 견적 자동 산출, BOM 관리 |
| 입고·재고 | 입고 LOT 등록, 재고 조회, 공급처 품질 분석 |
| 공정·생산 | 작업지시 관리, 생산 LOT 실적, 포밍/용접 공정 데이터 |
| 품질검사 | 검사 결과 등록, 불량 이력, 품질 기준 조회 |
| 출하·물류 | 출하 지시, LOT 추적, 클레임 관리 |
| 설비·IoT | 설비 상태 조회, 센서 데이터 스트림, 이상 감지 |
| AI Agent | RAG 자연어 질의, CAD AI 트리거, KPI 조회 |
| 시스템관리 | 인증, 사용자 관리, 알림, 시스템 로그 |

## Tech Stack (from spec.md)

- **Framework**: FastAPI (Python)
- **Auth**: JWT Bearer Token
- **DB**: PostgreSQL + pgvector (TimescaleDB for IoT)
- **File Storage**: S3 (CAD 도면, 비드 이미지)
- **Realtime**: WebSocket (설비 현황판, 알림)
- **AI**: LangChain/LangGraph (RAG), XGBoost (견적), YOLOv8 (CAD Vision)

## Success Criteria

- 모든 MES 모듈 기능이 API로 커버됨
- CAD 도면 업로드 → 견적 자동 산출 엔드투엔드 플로우 정의
- LOT 기반 Traceability 조회 API 명세 완료
- AI Agent 자연어 질의 API 명세 완료
