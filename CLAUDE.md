# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Buyoung AI MES** — Manufacturing AI-specialized Smart Factory system for Buyoung Corporation (주식회사 부영기업). This is a Korean manufacturing company building an AI-driven Manufacturing Execution System (MES). The formal business plan is in `docs/` as a PDF (Korean, dated 2026-05-11).

The project is in **early planning phase** (PDCA Phase 1). No application source code exists yet.

## Development Framework

This project uses the **bkit (Buildkit)** framework with **oh-my-claudecode (OMC)** for AI-driven development:

- Development follows the **PDCA cycle** (Plan → Do → Check → Act)
- Current phase: `plan` (Dynamic level)
- Use `/pdca plan`, `/pdca design`, `/pdca do`, `/pdca analyze` to progress through phases
- Agent state is tracked in `.bkit/agent-state.json` and `.omc/state/`

## Project Context

- **Domain**: Smart factory / MES for manufacturing (제조 AI 특화 스마트공장)
- **Language**: Korean business context; code and documentation may be bilingual
- **Level**: Dynamic (fullstack with backend services, not enterprise microservices)
- **Business plan reference**: `[사업계획서] 제조AI특화 스마트공장 사업계획서_주식회사 부영기업_20260511.pdf`

## Project Documents

- `docs/intro.md` — 프로젝트 소개: 회사 개요, 사업 목표, 공정 흐름, AI 적용 공정 요약, 핵심 KPI
- `docs/problem.md` — 현황 문제 분석: 공정별 AS-IS 문제(수주~출하), 데이터 구조 문제, 기존 시스템 현황
- `docs/spec.md` — 시스템 명세: 아키텍처, CAD 견적 AI 파이프라인, RAG AI Agent, 클라우드 인프라, 앱 모듈, 사업비, 구현 일정
- `docs/erd.md` — ERD 설계: 9개 도메인 35개 테이블 (Mermaid 다이어그램 + 컬럼 정의 + 인덱스 전략 + 설계 결정 사항)
- `docs/01-plan/features/api-design.plan.md` — API 설계 Plan 문서
- `docs/02-design/features/api-design.design.md` — REST API 전체 설계 (FastAPI 기반, 8개 도메인 + AI Agent + WebSocket + 핵심 플로우 3종)

## Development Approach

Since no tech stack is chosen yet, decisions should align with:
1. Reading the business plan PDF first to understand MES requirements before proposing architecture
2. Dynamic-level tooling (e.g., Next.js + bkend.ai or similar BaaS) unless requirements demand otherwise
3. Korean language support throughout the UI

## State Files (Do Not Edit Manually)

- `.bkit/agent-state.json` — bkit team and PDCA phase state
- `.omc/state/mission-state.json` — running agent missions
- `docs/.pdca-status.json` — PDCA phase tracking
- `docs/.bkit-memory.json` — session memory for bkit agents
