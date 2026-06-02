# Gap Analysis Report: api-design

- **분석일**: 2026-06-02
- **Match Rate**: 62%
- **상태**: ⚠️ 개선 필요 (< 90%)

---

## Match Rate 상세

| 항목 | 점수 | 상태 |
|------|:----:|:----:|
| 엔드포인트 구현률 | 58% (44/76) | ⚠️ |
| 응답/에러 포맷 일치 | 100% | ✅ |
| 라우팅 경로 정합성 | 70% | ⚠️ |
| **종합** | **62%** | ⚠️ |

---

## 구현 완료 도메인

| 도메인 | 상태 |
|--------|------|
| 인증 (Auth) | ✅ 4/4 |
| 입고 (Receiving) | ✅ 5/5 |
| 설비 (Equipment) | ✅ 4/4 |
| WebSocket | ✅ 3/3 |
| 응답/에러 포맷 | ✅ 완벽 일치 |
| AI Agent | ✅ 7/7 |
| CAD | ✅ 4/5 |
| 수주/견적/BOM | ⚠️ 부분 |
| 생산 | ⚠️ 부분 |
| 출하/클레임 | ⚠️ 부분 |
| 품질 | ⚠️ 부분 |

---

## 갭 목록

### 🔴 P1 — 핵심 플로우 차단 (즉시 필요)

| 항목 | 상세 |
|------|------|
| `PUT /quotes/{id}/approve` | 견적 승인 — 플로우1 완결 차단 |
| `PUT /quotes/{id}/reject` | 견적 거절 미구현 |
| `GET /quotes/{id}` | 견적 단건 조회 전역 경로 없음 |
| Customer 경로 오류 | `/v1/customers` 설계 → 실제 `/v1/orders/customers` |
| Work Orders 라우터 전체 | 플로우2(Traceability) 시작점 차단 |

### 🟡 P2 — 도메인 전체 미구현

| 도메인 | 미구현 엔드포인트 수 |
|--------|---------------------|
| Supplier (공급처) | 4개 (`GET/POST /suppliers`, `GET /{id}`, `GET /{id}/quality`) |
| Material (원자재) | 4개 (`GET/POST /materials`, `GET /{code}`, `GET /{code}/stock`) |
| Inventory (재고) | 3개 (`GET /inventory`, `GET /{code}`, `POST /check-availability`) |

### 🟡 P2 — 개별 미구현

| 항목 | 설명 |
|------|------|
| `GET /production-lots` | 생산 LOT 목록 조회 없음 |
| `POST /production-lots` | 생산 LOT 생성 없음 |
| `PUT /shipping-orders/{id}/ship` | 출하 확정 미구현 |
| `GET /shipping-orders/{id}/lots` | 출하 LOT 목록 조회 없음 |
| `PUT /shipping-lots/{id}/tracking` | 운송장 번호 등록 미구현 |
| `GET /claims` | 클레임 목록 조회 없음 |
| `PUT /claims/{id}/investigate` | 클레임 조사 미구현 |
| `PUT /claims/{id}/resolve` | 클레임 종결 미구현 |

### 🟢 P3 — 운영/관리

| 도메인 | 미구현 |
|--------|--------|
| 알림 (Alerts) | 전체 (`GET /alerts`, `PUT /{id}/acknowledge`, `GET /unread-count`) |
| 시스템 관리 | 전체 (`GET/POST /users`, `PUT/DELETE /{id}`, `GET /system-logs`) |

---

## 라우팅 경로 불일치

| 설계 경로 | 실제 경로 | 영향 |
|-----------|-----------|------|
| `/v1/customers` | `/v1/orders/customers` | High |
| `/v1/quotes/{id}` | 미구현 | High |
| `/v1/kpi/*` | `/v1/ai/kpi/*` | Medium |

---

## 핵심 플로우 검증

| 플로우 | 상태 | 차단 원인 |
|--------|------|-----------|
| 플로우1 (CAD→견적) | ⚠️ 부분 | `PUT /quotes/{id}/approve` 미구현 |
| 플로우2 (LOT 추적) | ⚠️ 부분 | `POST /work-orders` 미구현 |
| 플로우3 (AI 입고 품질) | ✅ 완료 | - |

---

## 추가 구현 항목 (설계 외)

| 항목 | 비고 |
|------|------|
| `GET /health` | 헬스체크 (설계에 추가 권장) |
| `GET /quality-inspections/{id}/defects` | 설계에 추가 권장 |
| CAD dxf 형식 허용 | 설계 업데이트 필요 |

---

## 권장 조치

> Match Rate 62% — `/pdca iterate api-design` 으로 P1 항목 자동 보완 권장
> 또는 스코프를 조정하여 설계 문서를 현재 구현 기준으로 업데이트
