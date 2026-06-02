# [Design] API Design — 부영기업 AI MES REST API

> Phase: Design | Feature: api-design | 참조: erd.md, spec.md

---

## 1. API 아키텍처 개요

```
Client (Web / POP / 스마트패드 / 모바일)
        │
        ▼
  [ Nginx Reverse Proxy ]
        │
        ▼
  [ FastAPI AP Server ]  ──── REST API (JSON)
        │                ──── WebSocket (실시간 현황판·알림)
        │                ──── SSE (CAD 파싱 진행상황)
        ├── PostgreSQL (정형 데이터)
        ├── pgvector (RAG 임베딩)
        ├── TimescaleDB (IoT 센서)
        └── S3 (CAD 도면, 비드 이미지)
              │
              ▼
        [ AI Server ]
        LangChain RAG / XGBoost / YOLOv8
```

**Base URL**: `https://api.buyoung-mes.com/v1`

**Content-Type**: `application/json` (파일 업로드는 `multipart/form-data`)

---

## 2. 인증 (Authentication)

### 2-1. JWT Bearer Token

모든 API는 `Authorization: Bearer {token}` 헤더 필수.

### 2-2. 엔드포인트

```
POST   /auth/login          # 로그인 → access_token + refresh_token
POST   /auth/refresh        # 토큰 갱신
POST   /auth/logout         # 로그아웃 (refresh_token 무효화)
GET    /auth/me             # 내 프로필 조회
```

#### POST /auth/login

**Request**
```json
{
  "username": "operator01",
  "password": "password"
}
```

**Response 200**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "user_id": "uuid",
    "username": "operator01",
    "role": "OPERATOR",
    "department": "생산부"
  }
}
```

### 2-3. 역할 (Role)

| Role | 설명 |
|------|------|
| ADMIN | 전체 권한 |
| MANAGER | 조회·승인·설정 |
| OPERATOR | 생산·입출고 실적 입력 |
| INSPECTOR | 품질 검사 결과 입력 |

---

## 3. 공통 규격

### 응답 형식

```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 150
  }
}
```

### 에러 형식

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "수주 정보를 찾을 수 없습니다.",
    "detail": "order_id: abc123"
  }
}
```

### 에러 코드

| HTTP | code | 설명 |
|------|------|------|
| 400 | VALIDATION_ERROR | 요청 파라미터 오류 |
| 401 | UNAUTHORIZED | 인증 토큰 없음·만료 |
| 403 | FORBIDDEN | 권한 없음 |
| 404 | NOT_FOUND | 리소스 없음 |
| 409 | CONFLICT | 중복 데이터 |
| 422 | BUSINESS_ERROR | 비즈니스 규칙 위반 |
| 500 | INTERNAL_ERROR | 서버 오류 |

### 페이지네이션 (Query Parameters)

| 파라미터 | 기본값 | 설명 |
|----------|--------|------|
| `page` | 1 | 페이지 번호 |
| `limit` | 20 | 페이지 당 건수 (max 100) |
| `sort` | `created_at` | 정렬 컬럼 |
| `order` | `desc` | 정렬 방향 |

---

## 4. 수주·견적 API

### 4-1. 고객사 (Customer)

```
GET    /customers                    # 고객사 목록
POST   /customers                    # 고객사 등록
GET    /customers/{customer_id}      # 고객사 상세
PUT    /customers/{customer_id}      # 고객사 수정
DELETE /customers/{customer_id}      # 고객사 삭제 (소프트)
```

### 4-2. 수주 (Order)

```
GET    /orders                       # 수주 목록 (필터: status, customer_id, date_range)
POST   /orders                       # 수주 등록
GET    /orders/{order_id}            # 수주 상세
PUT    /orders/{order_id}            # 수주 수정
GET    /orders/{order_id}/traceability  # 수주 전체 이력 (Digital Thread)
```

#### POST /orders

**Request**
```json
{
  "customer_id": "uuid",
  "product_type": "LADDER_TRAY",
  "product_spec": {
    "width_mm": 200,
    "thickness_mm": 2.0,
    "material": "SS400",
    "length_mm": 3000
  },
  "requested_delivery_date": "2026-08-01",
  "quantity": 100
}
```

**Response 201**
```json
{
  "success": true,
  "data": {
    "order_id": "uuid",
    "order_no": "ORD-2026-001234",
    "status": "RECEIVED",
    ...
  }
}
```

#### GET /orders/{order_id}/traceability

LOT 기반 전 공정 추적 (Digital Thread).

**Response 200**
```json
{
  "success": true,
  "data": {
    "order_id": "uuid",
    "order_no": "ORD-2026-001234",
    "cad_drawing": { "drawing_no": "DWG-001", "parse_status": "COMPLETED" },
    "quote": { "quote_no": "QTE-001", "total_amount": 1500000 },
    "bom": { "bom_version": "v1", "line_count": 5 },
    "work_order": { "work_order_no": "WO-001", "status": "COMPLETED" },
    "production_lots": [
      {
        "production_lot_no": "PL-001",
        "process_type": "FORMING",
        "actual_qty": 100,
        "defect_qty": 2
      }
    ],
    "quality_inspections": [
      { "inspection_type": "FINAL", "result": "PASS" }
    ],
    "shipping": {
      "shipping_order_no": "SHP-001",
      "shipped_date": "2026-07-30"
    }
  }
}
```

### 4-3. CAD 도면 (CAD Drawing)

```
POST   /orders/{order_id}/cad-drawings          # CAD 도면 업로드
GET    /orders/{order_id}/cad-drawings          # 도면 목록
GET    /cad-drawings/{drawing_id}               # 도면 상세 (파싱 결과 포함)
POST   /cad-drawings/{drawing_id}/parse         # 파싱 재실행 (수동 트리거)
GET    /cad-drawings/{drawing_id}/parse-status  # 파싱 상태 확인 (폴링용)
```

#### POST /orders/{order_id}/cad-drawings

**Request** `multipart/form-data`
```
file: [DWG or PDF 파일]
drawing_no: "DWG-2026-001"
```

**Response 202** (비동기 파싱 시작)
```json
{
  "success": true,
  "data": {
    "drawing_id": "uuid",
    "drawing_no": "DWG-2026-001",
    "file_type": "DWG",
    "parse_status": "PENDING",
    "message": "CAD 파싱이 시작되었습니다. parse-status 엔드포인트로 진행상황을 확인하세요."
  }
}
```

#### GET /cad-drawings/{drawing_id}

**Response 200** (파싱 완료 후)
```json
{
  "success": true,
  "data": {
    "drawing_id": "uuid",
    "parse_status": "COMPLETED",
    "confidence_score": 0.94,
    "parsed_objects": {
      "holes": [{ "x": 100, "y": 200, "diameter_mm": 12 }],
      "slots": [...],
      "total_length_mm": 3000,
      "thickness_mm": 2.0,
      "material": "SS400",
      "bend_count": 4
    },
    "parsed_at": "2026-06-01T10:30:00Z"
  }
}
```

### 4-4. 견적 (Quote)

```
POST   /orders/{order_id}/quotes          # 견적 자동 산출 트리거
GET    /orders/{order_id}/quotes          # 견적 목록
GET    /quotes/{quote_id}                 # 견적 상세 (SHAP 설명 포함)
PUT    /quotes/{quote_id}/approve         # 견적 승인 (MANAGER 권한)
PUT    /quotes/{quote_id}/reject          # 견적 반려
```

#### POST /orders/{order_id}/quotes

CAD 파싱 완료 후 XGBoost 기반 견적 자동 산출.

**Request**
```json
{
  "drawing_id": "uuid",
  "material_price_override": null
}
```

**Response 201**
```json
{
  "success": true,
  "data": {
    "quote_id": "uuid",
    "quote_no": "QTE-2026-0045",
    "total_amount": 1523400,
    "material_cost": 980000,
    "process_cost": 543400,
    "process_cost_breakdown": {
      "forming": 180000,
      "welding": 240000,
      "cutting": 123400
    },
    "estimated_lead_time_days": 5,
    "confidence_score": 0.91,
    "shap_explanation": {
      "top_features": [
        { "feature": "total_length_mm", "impact": 0.35, "value": 3000 },
        { "feature": "bend_count", "impact": 0.22, "value": 4 },
        { "feature": "material_SS400", "impact": 0.18, "value": 1 }
      ]
    },
    "status": "AUTO"
  }
}
```

### 4-5. BOM

```
GET    /orders/{order_id}/bom             # BOM 조회
POST   /orders/{order_id}/bom/generate   # BOM 자동 생성 (GNN 기반)
PUT    /bom/{bom_id}/lines/{line_id}     # BOM 라인 수정
POST   /bom/{bom_id}/confirm             # BOM 확정
```

---

## 5. 입고·재고 API

### 5-1. 공급처 (Supplier)

```
GET    /suppliers                        # 공급처 목록
POST   /suppliers                        # 공급처 등록
GET    /suppliers/{supplier_id}          # 공급처 상세
GET    /suppliers/{supplier_id}/quality  # 공급처 품질 분석 (불량률 추이)
```

### 5-2. 원자재 (Material)

```
GET    /materials                        # 원자재 목록 (필터: material_type)
POST   /materials                        # 원자재 등록
GET    /materials/{material_code}        # 원자재 상세
GET    /materials/{material_code}/stock  # 재고 현황
```

### 5-3. 입고 LOT (Receiving Lot)

```
GET    /receiving-lots                        # 입고 LOT 목록
POST   /receiving-lots                        # 입고 LOT 등록 (스마트패드)
GET    /receiving-lots/{lot_id}               # LOT 상세
PUT    /receiving-lots/{lot_id}/inspection    # 입고 검사 결과 등록
GET    /receiving-lots/{lot_id}/traceability  # LOT 사용 이력 추적
```

#### POST /receiving-lots

**Request**
```json
{
  "supplier_id": "uuid",
  "material_code": "MAT-SS400-2T",
  "lot_no": "LOT-2026-0601-001",
  "received_date": "2026-06-01",
  "quantity": 50.0,
  "weight_kg": 235.5,
  "thickness_mm": 2.0,
  "storage_location": "A-03-02"
}
```

### 5-4. 재고 (Inventory)

```
GET    /inventory                          # 전체 재고 현황
GET    /inventory/{material_code}          # 자재별 재고
POST   /inventory/check-availability      # 자재 가용 여부 일괄 확인 (작업지시용)
```

#### POST /inventory/check-availability

**Request**
```json
{
  "items": [
    { "material_code": "MAT-SS400-2T", "required_qty": 30.0 },
    { "material_code": "MAT-WIRE-0.8", "required_qty": 5.0 }
  ]
}
```

**Response 200**
```json
{
  "success": true,
  "data": {
    "all_available": false,
    "items": [
      { "material_code": "MAT-SS400-2T", "available": true, "quantity_available": 45.2 },
      { "material_code": "MAT-WIRE-0.8", "available": false, "quantity_available": 2.1, "shortage": 2.9 }
    ]
  }
}
```

---

## 6. 공정·생산 API

### 6-1. 작업지시 (Work Order)

```
GET    /work-orders                       # 작업지시 목록 (필터: status, date)
POST   /work-orders                       # 작업지시 생성
GET    /work-orders/{work_order_id}       # 작업지시 상세
PUT    /work-orders/{work_order_id}/start # 작업 시작
PUT    /work-orders/{work_order_id}/complete # 작업 완료
```

### 6-2. 생산 LOT (Production Lot)

```
GET    /production-lots                          # 생산 LOT 목록
POST   /production-lots                          # 생산 LOT 생성
GET    /production-lots/{lot_id}                 # LOT 상세
PUT    /production-lots/{lot_id}/actual-qty      # 실적 수량 업데이트 (POP)
```

### 6-3. 포밍 공정 데이터

```
POST   /production-lots/{lot_id}/forming         # 포밍 공정 데이터 등록 (IoT 수집)
GET    /production-lots/{lot_id}/forming         # 포밍 데이터 조회
GET    /equipment/{equipment_id}/forming/trend   # 설비별 포밍 조건 추이
```

#### POST /production-lots/{lot_id}/forming

PLC/IoT에서 자동 수집 또는 터치PC에서 수동 입력.

**Request**
```json
{
  "equipment_id": "uuid",
  "pressure_mpa": 12.5,
  "speed_mpm": 8.2,
  "temperature_c": 45.3,
  "bending_angle_deg": 90.0,
  "cut_length_mm": 3000,
  "defect_count": 0
}
```

### 6-4. 용접 공정 데이터

```
POST   /production-lots/{lot_id}/welding         # 용접 공정 데이터 등록
GET    /production-lots/{lot_id}/welding         # 용접 데이터 조회
POST   /production-lots/{lot_id}/welding/{id}/bead-image  # 비드 이미지 업로드
```

### 6-5. 포장 실적

```
POST   /production-lots/{lot_id}/packing         # 포장 실적 등록 (스마트패드)
GET    /production-lots/{lot_id}/packing         # 포장 현황
```

---

## 7. 품질검사 API

```
GET    /quality-inspections                          # 검사 목록
POST   /quality-inspections                          # 검사 결과 등록
GET    /quality-inspections/{inspection_id}          # 검사 상세
POST   /quality-inspections/{inspection_id}/defects  # 불량 이력 등록
GET    /production-lots/{lot_id}/quality-summary     # LOT 품질 요약
```

#### POST /quality-inspections

**Request**
```json
{
  "production_lot_id": "uuid",
  "qs_id": "uuid",
  "inspection_type": "FINAL",
  "result": "PASS",
  "remarks": "치수 정상, 용접 품질 양호"
}
```

#### POST /quality-inspections/{inspection_id}/defects

**Request**
```json
{
  "defect_type": "용접 결함",
  "defect_location": "좌측 모서리 용접부",
  "severity": "MINOR",
  "corrective_action": "재용접 후 재검사"
}
```

---

## 8. 출하·물류 API

### 8-1. 출하 지시 (Shipping Order)

```
GET    /shipping-orders                           # 출하 지시 목록 (필터: status, date, risk)
POST   /shipping-orders                           # 출하 지시 생성
GET    /shipping-orders/{shipping_order_id}       # 출하 상세
PUT    /shipping-orders/{shipping_order_id}/ship  # 출하 확정
GET    /shipping-orders/delivery-risk             # 납기 리스크 오더 목록
```

### 8-2. 출하 LOT

```
POST   /shipping-orders/{id}/lots                 # 출하 LOT 등록 (스캔)
GET    /shipping-orders/{id}/lots                 # 출하 LOT 목록
PUT    /shipping-lots/{lot_id}/tracking           # 운송장 번호 등록
```

### 8-3. 클레임 (Claim)

```
GET    /claims                           # 클레임 목록 (필터: status, severity)
POST   /claims                           # 클레임 등록
GET    /claims/{claim_id}               # 클레임 상세
PUT    /claims/{claim_id}/investigate   # 원인 분석 결과 등록
PUT    /claims/{claim_id}/resolve       # 클레임 종결
```

---

## 9. 설비·IoT API

### 9-1. 설비 (Equipment)

```
GET    /equipment                          # 설비 목록
GET    /equipment/{equipment_id}           # 설비 상세
PUT    /equipment/{equipment_id}/status    # 설비 상태 업데이트
GET    /equipment/{equipment_id}/sensor-data  # 센서 데이터 조회 (시계열)
```

#### GET /equipment/{equipment_id}/sensor-data

**Query Parameters**
| 파라미터 | 설명 | 예시 |
|----------|------|------|
| `from` | 시작 시각 (ISO8601) | `2026-06-01T08:00:00Z` |
| `to` | 종료 시각 | `2026-06-01T18:00:00Z` |
| `interval` | 집계 간격 | `1m` / `5m` / `1h` |
| `metrics` | 조회할 지표 | `pressure,speed,current` |

**Response 200**
```json
{
  "success": true,
  "data": {
    "equipment_id": "uuid",
    "interval": "5m",
    "series": [
      {
        "timestamp": "2026-06-01T08:00:00Z",
        "pressure_mpa": 12.3,
        "speed_mpm": 8.1,
        "current_a": 45.2,
        "anomaly_flag": false
      }
    ]
  }
}
```

### 9-2. WebSocket — 실시간 현황판

```
WS  /ws/dashboard          # 전체 KPI 실시간 스트림
WS  /ws/equipment/{id}     # 특정 설비 센서 실시간 스트림
WS  /ws/alerts             # 이상 알림 실시간 수신
```

**WS /ws/dashboard 메시지 형식**
```json
{
  "type": "KPI_UPDATE",
  "data": {
    "hourly_output": 18,
    "defect_rate": 0.012,
    "equipment_oee": 0.87,
    "active_work_orders": 3
  },
  "timestamp": "2026-06-01T10:00:00Z"
}
```

---

## 10. AI Agent API

### 10-1. RAG 자연어 질의

```
POST   /ai/query                    # AI Agent 자연어 질의 (입고·출하·공정)
GET    /ai/query-history            # 질의 이력 조회
PUT    /ai/query/{query_id}/feedback  # 응답 피드백 등록
```

#### POST /ai/query

**Request**
```json
{
  "agent_type": "INTEGRATED",
  "query": "LOT-2026-0601-001 원자재로 생산된 제품의 품질 검사 결과는?",
  "session_id": "sess-abc123"
}
```

**Response 200**
```json
{
  "success": true,
  "data": {
    "query_id": "uuid",
    "agent_type": "INTEGRATED",
    "response": "LOT-2026-0601-001 원자재(SS400, 2T)로 생산된 제품은 총 100ea이며, 최종 품질 검사 결과 PASS입니다. 불량 2ea(MINOR 등급)가 발생하였으나 재작업 후 합격 처리되었습니다.",
    "retrieved_sources": [
      { "type": "quality_inspection", "id": "uuid", "relevance": 0.92 },
      { "type": "defect_record", "id": "uuid", "relevance": 0.88 }
    ],
    "session_id": "sess-abc123"
  }
}
```

### 10-2. CAD 견적 AI

```
POST   /ai/cad-quote/trigger        # CAD 견적 AI 수동 트리거 (= /quotes POST와 동일)
GET    /ai/cad-quote/{quote_id}/explain  # SHAP 설명 상세 조회
```

#### GET /ai/cad-quote/{quote_id}/explain

**Response 200**
```json
{
  "success": true,
  "data": {
    "quote_id": "uuid",
    "total_amount": 1523400,
    "explanation": "총 견적금액 1,523,400원의 주요 원가 요인은 다음과 같습니다:\n1. 제품 총 길이(3,000mm): 원가의 35% 영향\n2. 절곡 횟수(4회): 원가의 22% 영향\n3. 재질(SS400): 원가의 18% 영향",
    "shap_features": [
      { "feature": "total_length_mm", "value": 3000, "impact_pct": 35, "direction": "+" },
      { "feature": "bend_count", "value": 4, "impact_pct": 22, "direction": "+" },
      { "feature": "hole_count", "value": 12, "impact_pct": 11, "direction": "+" }
    ]
  }
}
```

### 10-3. KPI API

```
GET    /kpi/summary                 # KPI 대시보드 요약
GET    /kpi/records                 # KPI 이력 (필터: type, period, process_area)
POST   /kpi/records                 # KPI 수동 등록 (배치)
```

#### GET /kpi/summary

**Response 200**
```json
{
  "success": true,
  "data": {
    "period": "2026-06-01",
    "hourly_output": {
      "target": 18, "actual": 17.2, "status": "AT_RISK", "unit": "ea/h"
    },
    "lead_time": {
      "target": 60, "actual": 58, "status": "ON_TRACK", "unit": "h"
    },
    "defect_rate": {
      "target": 0.02, "actual": 0.012, "status": "ON_TRACK", "unit": "%"
    }
  }
}
```

---

## 11. 알림 API

```
GET    /alerts                          # 알림 목록 (미확인 우선)
PUT    /alerts/{alert_id}/acknowledge  # 알림 확인 처리
GET    /alerts/unread-count            # 미확인 알림 수
```

---

## 12. 시스템관리 API

```
GET    /users                          # 사용자 목록 (ADMIN)
POST   /users                          # 사용자 등록
PUT    /users/{user_id}                # 사용자 수정
DELETE /users/{user_id}                # 사용자 비활성화
GET    /system-logs                    # 시스템 로그 조회 (필터: action, user_id, date)
```

---

## 13. 핵심 플로우 정의

### 플로우 1: CAD 도면 → 견적 자동 산출

```
① POST /orders                          수주 등록
② POST /orders/{id}/cad-drawings        CAD 도면 업로드 → 202 Accepted
③ GET  /cad-drawings/{id}/parse-status  파싱 완료 확인 (폴링 또는 WS)
④ POST /orders/{id}/quotes              견적 자동 산출 트리거
⑤ GET  /quotes/{id}                     견적 결과 + SHAP 설명 조회
⑥ PUT  /quotes/{id}/approve             견적 승인
⑦ POST /orders/{id}/bom/generate        BOM 자동 생성
```

### 플로우 2: 생산 LOT 이력 추적 (Traceability)

```
① POST /receiving-lots                  원자재 입고 LOT 등록
② POST /work-orders                     작업지시 생성 (BOM → 자재 예약)
③ POST /production-lots                 생산 LOT 생성
④ POST /production-lots/{id}/forming    포밍 공정 데이터 등록
⑤ POST /production-lots/{id}/welding    용접 공정 데이터 등록
⑥ POST /quality-inspections            최종 품질 검사
⑦ POST /production-lots/{id}/packing   포장 실적 등록
⑧ POST /shipping-orders/{id}/lots      출하 스캔
⑨ GET  /orders/{id}/traceability        전 공정 이력 조회
```

### 플로우 3: AI Agent 입고 품질 판단

```
① POST /receiving-lots                  입고 LOT 스캔 등록
② POST /ai/query                        "LOT-xxx 입고 품질 기준 만족하나요?"
③ (RAG Agent: Vector DB 검색 → 품질기준서 + 공급처 이력 조회)
④ Response: 품질 판정 결과 + 대응 가이드
⑤ PUT  /receiving-lots/{id}/inspection  최종 검사 결과 등록
```

---

## 14. 파일 업로드 규격

| 용도 | 엔드포인트 | 허용 형식 | 최대 크기 |
|------|-----------|-----------|-----------|
| CAD 도면 | POST /orders/{id}/cad-drawings | DWG, PDF | 50 MB |
| 비드 이미지 | POST /production-lots/{id}/welding/{id}/bead-image | JPG, PNG | 10 MB |

파일은 S3에 저장, DB에는 경로만 보관.

---

## 15. 구현 우선순위

| 우선순위 | 도메인 | 이유 |
|----------|--------|------|
| P1 | 인증 + 수주·견적 + CAD AI | 핵심 사업 목표 (견적 자동화) |
| P1 | 입고·재고 + AI Agent (입고) | LOT Traceability 시작점 |
| P2 | 공정·생산 + 설비 IoT | 생산 가시성 확보 |
| P2 | 품질검사 + 출하·물류 + AI Agent (출하) | Traceability 완성 |
| P3 | KPI + 알림 + WebSocket | 대시보드 실시간화 |
| P3 | 시스템관리 | 운영 안정화 |
