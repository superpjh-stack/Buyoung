"""설계단계 5개 산출물 생성 SF-TD1~TD5"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUT = os.path.dirname(os.path.abspath(__file__))
BLUE = RGBColor(0, 70, 127)


def cover(doc, title, doc_no):
    for _ in range(4): doc.add_paragraph()
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title); r.font.size = Pt(24); r.font.bold = True; r.font.color.rgb = BLUE
    doc.add_paragraph()
    p2 = doc.add_paragraph(); p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.add_run("주식회사 부영기업\n제조AI 특화 스마트공장 MES 구축 사업").font.size = Pt(13)
    doc.add_paragraph()
    p3 = doc.add_paragraph(); p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.add_run(f"문서번호: {doc_no}\n버전: v1.0\n작성일: 2026-06-03\n작성기관: (주)AI솔루션파트너스")
    doc.add_page_break()


def history(doc):
    doc.add_heading("문서 이력", level=1)
    t = doc.add_table(rows=2, cols=5); t.style = "Table Grid"
    for i, h in enumerate(["버전","작성일","작성자","검토자","내용"]):
        t.rows[0].cells[i].text = h
    t.rows[1].cells[0].text = "v1.0"; t.rows[1].cells[1].text = "2026-06-03"
    t.rows[1].cells[2].text = "홍길동"; t.rows[1].cells[3].text = "김철수"
    t.rows[1].cells[4].text = "최초 작성"
    doc.add_paragraph()


def add_table(doc, headers, rows):
    t = doc.add_table(rows=1+len(rows), cols=len(headers)); t.style = "Table Grid"
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]; c.text = h
        for run in c.paragraphs[0].runs: run.font.bold = True
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row): t.rows[ri+1].cells[ci].text = str(val)
    doc.add_paragraph()


def new_doc():
    doc = Document()
    s = doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
    for m in ("top","bottom","left","right"): setattr(s, m+"_margin", Cm(2.5))
    return doc


# ─────────────────── SF-TD1 개선업무설계서 ───────────────────────────────
doc = new_doc(); cover(doc, "개선업무설계서", "SF-TD1"); history(doc)

doc.add_heading("1. 개선 업무 개요", level=1)
add_table(doc, ["항목","내용"],
    [["개선 목적","AI 기술 기반 제조 업무 전 과정 자동화 및 데이터 기반 의사결정 지원"],
     ["개선 범위","수주접수~출하까지 7개 공정 전 과정"],
     ["핵심 개선","CAD AI 견적(94% 시간 단축), LOT Digital Thread, 실시간 KPI 대시보드"],
     ["기대효과","납기 준수율 20%p 향상, 불량률 60% 감소, 생산성 18% 향상"]])

doc.add_heading("2. TO-BE 전체 업무 흐름도", level=1)
doc.add_paragraph("[ 수주접수 ] → [ CAD AI 분석 ] → [ 자동 견적 산출 ] → [ 견적 승인 ]")
doc.add_paragraph("     ↓")
doc.add_paragraph("[ BOM 자동 생성 ] → [ 작업지시 생성 ] → [ 생산/공정 실적 수집 ]")
doc.add_paragraph("     ↓")
doc.add_paragraph("[ 공정별 품질 검사 ] → [ 출하 LOT 배정 ] → [ 출하 완료 ]")
doc.add_paragraph("     ↕ (모든 단계에서 AI Agent 자연어 질의 가능)")

doc.add_heading("3. 공정별 상세 개선 업무 절차", level=1)
add_table(doc, ["공정","AS-IS 절차","TO-BE 절차","개선 포인트"],
    [
        ["수주접수","이메일 수신→수기 입력→담당자 배정","시스템 수주 등록→자동 알림→AI 견적 트리거","실시간 처리, 누락 방지"],
        ["CAD AI 분석","도면 수동 검토 (1~2일)","DWG/PDF 업로드→AI 자동 파싱 (30분)","YOLOv8 객체 인식, 치수 자동 추출"],
        ["자동 견적","엑셀 수동 계산 (2~3일)","XGBoost 자동 산출 (즉시)→SHAP 설명","견적 정확도 95%, 시간 94% 단축"],
        ["BOM 생성","수동 BOM 작성 (4시간)","GNN 기반 자동 BOM 생성 (즉시)","누락 방지, 버전 관리 자동화"],
        ["작업지시","구두/메모 전달","시스템 작업지시 생성→담당자 알림","LOT 기반 추적 시작"],
        ["생산/공정","수기 실적 기록","IoT 센서→자동 실적 수집→AI 이상 감지","실시간 모니터링, 예방 정비"],
        ["품질검사","수기 대장 기록","검사 결과 시스템 등록→AI 불량 분석","LOT별 품질 이력 자동 추적"],
        ["출하","수동 출하 서류 작성","LOT 배정→검사 합격 확인→출하 확정","납기 리스크 AI 사전 감지"],
    ])

doc.add_heading("4. 개선 전/후 KPI 비교표", level=1)
add_table(doc, ["KPI 지표","현재(AS-IS)","목표(TO-BE)","개선율"],
    [
        ["견적 소요시간","2~3일","0.5시간","94% 단축"],
        ["BOM 작성시간","4시간","즉시 자동","100% 단축"],
        ["불량률","5%","2%","60% 감소"],
        ["납기 준수율","70%","90%","29%p 향상"],
        ["생산성 (시간당 생산량)","15 ea/h","18 ea/h","20% 향상"],
        ["LOT 이력 추적률","0%","100%","완전 추적"],
        ["AI 질의 응답시간","N/A","3초 이내","신규"],
    ])
doc.save(f"{OUT}/SF-TD1_개선업무설계서.docx")
print("[OK] SF-TD1_개선업무설계서.docx")


# ─────────────────── SF-TD2 아키텍처설계서 ───────────────────────────────
doc = new_doc(); cover(doc, "아키텍처설계서", "SF-TD2"); history(doc)

doc.add_heading("1. 시스템 아키텍처 개요", level=1)
doc.add_paragraph("본 시스템은 AWS 클라우드 기반의 3-Tier 아키텍처로 구성됩니다.")
doc.add_paragraph("프레젠테이션 계층: Next.js 16 (React 기반 SPA)")
doc.add_paragraph("비즈니스 로직 계층: FastAPI (Python 3.13, 비동기 처리)")
doc.add_paragraph("데이터 계층: PostgreSQL 17 + pgvector + Redis")

doc.add_heading("2. H/W 구성도 및 장비 규격", level=1)
doc.add_paragraph("[인터넷] → [AWS CloudFront] → [ECS Fargate] → [RDS PostgreSQL] → [ElastiCache Redis]")
doc.add_paragraph("                                      ↕")
doc.add_paragraph("              [현장 PLC] ─OPC-UA/Modbus─ [IoT Gateway (Raspberry Pi)]")
add_table(doc, ["구분","장비명/서비스","사양","수량","역할"],
    [
        ["클라우드 서버","AWS ECS Fargate","2vCPU/4GB (Task)","2","FastAPI WAS"],
        ["클라우드 DB","AWS RDS PostgreSQL 17","db.t3.medium 4vCPU/8GB","1","메인 DB"],
        ["클라우드 캐시","AWS ElastiCache Redis 7","cache.t3.micro","1","세션/캐시"],
        ["파일 스토리지","AWS S3","Standard 스토리지","1","CAD 파일 저장"],
        ["CDN","AWS CloudFront","글로벌 배포","1","정적 파일/API 캐시"],
        ["IoT 게이트웨이","Raspberry Pi 4 (4GB)","4-core ARM/4GB","5","PLC 데이터 수집"],
        ["클라이언트 PC","Windows 11 PC","Intel i5/16GB/SSD","10","사용자 단말"],
        ["네트워크 스위치","L2 Switch","1Gbps 24포트","2","현장 네트워크"],
    ])

doc.add_heading("3. S/W 구성도", level=1)
add_table(doc, ["계층","기술/SW","버전","라이선스","역할"],
    [
        ["프론트엔드","Next.js","16.2.7","MIT","UI/UX 프레임워크"],
        ["프론트엔드","React","19.x","MIT","컴포넌트 라이브러리"],
        ["프론트엔드","Tailwind CSS","3.x","MIT","CSS 프레임워크"],
        ["백엔드","FastAPI","0.115","MIT","REST API 서버"],
        ["백엔드","SQLAlchemy","2.0","MIT","ORM (비동기)"],
        ["AI/ML","XGBoost","2.1","Apache 2.0","견적 예측 모델"],
        ["AI/ML","LangChain","0.3","MIT","RAG AI Agent"],
        ["AI/ML","YOLOv8","8.3","AGPL-3.0","CAD 객체 인식"],
        ["DB","PostgreSQL","17","PostgreSQL","메인 RDB"],
        ["DB","pgvector","0.3","MIT","벡터 DB (AI 임베딩)"],
        ["캐시","Redis","7.x","BSD","세션/캐시"],
        ["인증","JWT (python-jose)","3.3","MIT","사용자 인증"],
        ["파일","Boto3 (AWS SDK)","1.35","Apache 2.0","S3 파일 업로드"],
    ])

doc.add_heading("4. N/W 구성도", level=1)
doc.add_paragraph("[외부 사용자] → HTTPS → [AWS CloudFront] → [ALB] → [ECS FastAPI]")
doc.add_paragraph("[ECS FastAPI] → [RDS PostgreSQL (Private Subnet)]")
doc.add_paragraph("[ECS FastAPI] → [ElastiCache Redis (Private Subnet)]")
doc.add_paragraph("[현장 IoT] → OPC-UA/Modbus → [Raspberry Pi] → MQTT → [AWS IoT Core] → [ECS]")

doc.add_heading("5. 보안 설계", level=1)
add_table(doc, ["보안 항목","적용 기술","상세 내용"],
    [
        ["인증","JWT (RS256)","Access Token 60분, Refresh Token 7일"],
        ["인가","RBAC","ADMIN/MANAGER/OPERATOR/INSPECTOR 4개 역할"],
        ["통신 암호화","TLS 1.3","모든 외부 통신 HTTPS 필수"],
        ["비밀번호","bcrypt","salt rounds 12"],
        ["SQL 인젝션","SQLAlchemy ORM","파라미터 바인딩으로 방어"],
        ["CORS","FastAPI CORSMiddleware","허용 도메인 화이트리스트"],
    ])
doc.save(f"{OUT}/SF-TD2_아키텍처설계서.docx")
print("[OK] SF-TD2_아키텍처설계서.docx")


# ─────────────────── SF-TD3 화면설계서 ───────────────────────────────────
doc = new_doc(); cover(doc, "화면설계서", "SF-TD3"); history(doc)

doc.add_heading("1. 화면 표준", level=1)
add_table(doc, ["항목","기준"],
    [
        ["해상도","최적: 1920×1080 / 최소: 1280×720"],
        ["브라우저","Chrome/Edge 최신 버전"],
        ["Primary Color","#2563eb (Blue-600)"],
        ["Secondary Color","#64748b (Slate-500)"],
        ["Danger Color","#ef4444 (Red-500)"],
        ["Success Color","#22c55e (Green-500)"],
        ["폰트","Geist Sans (기본), 맑은 고딕 (대체)"],
        ["기본 폰트 크기","14px (본문), 24px (페이지 제목), 12px (보조)"],
        ["사이드바 너비","224px (14rem), 다크 배경 (#111827)"],
        ["컨텐츠 패딩","24px (1.5rem)"],
    ])

doc.add_heading("2. 메뉴 구조도", level=1)
add_table(doc, ["No","메뉴명","URL","주요 기능","접근 권한"],
    [
        ["1","AI 대시보드","/","KPI 카드, 생산현황, 설비현황, 출하현황","ALL"],
        ["2","입고재고관리","/receiving","입고관리, 원자재이력, 공급처품질, 재고현황","ALL"],
        ["3","수주견적AI관리","/orders","수주목록, CAD분석, 견적관리, BOM","ALL"],
        ["4","출하물류관리","/shipping","출하지시, LOT추적, 클레임관리","ALL"],
        ["5","공정관리","/production","작업지시, 공정실적, 데이터모니터링, 이력조회","OPERATOR+"],
        ["6","AI Agent 통합","/ai","자연어질의, 생산분석, 의사결정지원","ALL"],
        ["7","KPI관리","/kpi","생산성KPI, 품질KPI, KPI목표설정","MANAGER+"],
        ["8","기준정보관리","/standards","품질기준, 작업표준, 코드관리","MANAGER+"],
        ["9","데이터관리","/data","데이터조회, 시각화, 다운로드","MANAGER+"],
        ["10","시스템관리","/admin","사용자관리, 시스템로그, 알림설정","ADMIN"],
    ])

doc.add_heading("3. 주요 화면 설계", level=1)
doc.add_heading("3.1 AI 대시보드 (/)"), None
add_table(doc, ["구성요소","유형","내용","데이터 소스"],
    [
        ["KPI 카드 4개","카드","시간당생산량/리드타임/불량률/설비OEE","GET /v1/ai/kpi/summary"],
        ["생산현황 분석","카드그리드","공정별 작업중/완료/불량 수량","더미 데이터(추후 연동)"],
        ["출하현황 분석","테이블","PENDING 출하 목록","GET /v1/shipping-orders"],
        ["설비 현황","카드그리드","설비 10개 상태 (IDLE/RUNNING/ERROR)","GET /v1/equipment"],
    ])
doc.add_heading("3.2 수주견적AI관리 (/orders)"), None
add_table(doc, ["탭","구성요소","입력항목","출력항목"],
    [
        ["수주목록","테이블","검색(상태/기간)","수주번호, 고객사, 수량, 납기, 상태"],
        ["CAD 도면 분석","업로드폼","order_id, drawing_no, 파일(DWG/PDF)","파싱상태, 도면번호"],
        ["견적 관리","카드목록","order_id 입력","견적번호, 금액, 신뢰도, 승인/거절 버튼"],
        ["BOM","조회","order_id 입력","BOM 목록 또는 자동생성 버튼"],
    ])

doc.add_heading("4. 화면 전환 흐름", level=1)
doc.add_paragraph("로그인(/login) → AI대시보드(/) → 각 메뉴 페이지")
doc.add_paragraph("수주등록 → CAD업로드 → 파싱완료 → 견적확인 → 견적승인 → BOM생성 → 작업지시")

doc.save(f"{OUT}/SF-TD3_화면설계서.docx")
print("[OK] SF-TD3_화면설계서.docx")


# ─────────────────── SF-TD4 프로그램설계서 ───────────────────────────────
doc = new_doc(); cover(doc, "프로그램설계서", "SF-TD4"); history(doc)

doc.add_heading("1. 프로그램 목록 (주요 API)", level=1)
add_table(doc, ["API-ID","메서드","URL","기능명","담당모듈"],
    [
        ["API-001","POST","/v1/auth/login","로그인","auth"],
        ["API-002","GET","/v1/auth/me","내 정보 조회","auth"],
        ["API-003","POST","/v1/auth/refresh","토큰 갱신","auth"],
        ["API-004","GET","/v1/customers","고객사 목록","order"],
        ["API-005","GET","/v1/orders","수주 목록","order"],
        ["API-006","POST","/v1/orders","수주 등록","order"],
        ["API-007","GET","/v1/orders/{id}","수주 상세","order"],
        ["API-008","POST","/v1/orders/{id}/quotes","견적 생성(AI)","order/ai"],
        ["API-009","GET","/v1/quotes/{id}","견적 상세","order"],
        ["API-010","PUT","/v1/quotes/{id}/approve","견적 승인","order"],
        ["API-011","POST","/v1/cad-drawings","CAD 업로드","cad"],
        ["API-012","GET","/v1/cad-drawings/{id}/parse-status","파싱 상태","cad"],
        ["API-013","GET","/v1/receiving-lots","입고 LOT 목록","receiving"],
        ["API-014","POST","/v1/receiving-lots","입고 LOT 등록","receiving"],
        ["API-015","GET","/v1/suppliers","공급처 목록","receiving"],
        ["API-016","GET","/v1/suppliers/{id}/quality","공급처 품질","receiving"],
        ["API-017","GET","/v1/work-orders","작업지시 목록","production"],
        ["API-018","POST","/v1/work-orders","작업지시 생성","production"],
        ["API-019","PUT","/v1/work-orders/{id}/status","상태 변경","production"],
        ["API-020","POST","/v1/quality-inspections","품질검사 등록","quality"],
        ["API-021","GET","/v1/shipping-orders","출하 목록","shipping"],
        ["API-022","PUT","/v1/shipping-orders/{id}/ship","출하 확정","shipping"],
        ["API-023","GET","/v1/equipment","설비 목록","equipment"],
        ["API-024","GET","/v1/equipment/{id}/sensor-data","센서 데이터","equipment"],
        ["API-025","POST","/v1/ai/query","AI 질의","ai"],
        ["API-026","GET","/v1/ai/kpi/summary","KPI 요약","ai"],
        ["WS-001","WS","/ws/dashboard","KPI 실시간 스트림","websocket"],
        ["WS-002","WS","/ws/equipment/{id}","설비 센서 스트림","websocket"],
    ])

doc.add_heading("2. 모듈별 상세 설계", level=1)
doc.add_heading("2.1 CAD AI 모듈 (app/ai/cad_pipeline.py)", level=2)
doc.add_paragraph("처리 흐름: 파일 업로드 → S3 저장 → BackgroundTask 실행 → APS 변환 → YOLOv8 추론 → XGBoost 견적 → SHAP 설명 → DB 저장")
add_table(doc, ["함수명","입력","출력","설명"],
    [
        ["parse_cad_drawing","file_path: str","dict (파싱 결과)","CAD 도면 파싱 (S3→APS)"],
        ["detect_objects_yolo","image_bytes: bytes","list[dict]","YOLOv8 객체 검출"],
        ["predict_quote","parsed: dict","dict (견적 결과)","XGBoost 견적 예측"],
        ["run_cad_quote_pipeline","drawing_id, file_path","dict","전체 파이프라인 실행"],
    ])

doc.add_heading("2.2 RAG Agent 모듈 (app/ai/rag_agent.py)", level=2)
doc.add_paragraph("처리 흐름: 자연어 질의 → OpenAI 임베딩 → pgvector 유사도 검색 → LLM 답변 생성 → 이력 저장")

doc.add_heading("3. 인터페이스 설계", level=1)
add_table(doc, ["인터페이스명","유형","프로토콜","데이터형식","비고"],
    [
        ["PLC 연계","외부","OPC-UA/Modbus","Binary→JSON","Raspberry Pi 중계"],
        ["AWS S3","외부","HTTPS","Multipart/Binary","CAD 파일 저장"],
        ["OpenAI API","외부","HTTPS","JSON","GPT-4o-mini 사용"],
        ["Autodesk APS","외부","HTTPS","JSON/Binary","도면 변환 (구현 예정)"],
    ])

doc.add_heading("4. 공통 모듈 설계", level=1)
add_table(doc, ["모듈","위치","기능"],
    [
        ["응답 형식","app/common/response.py","ok(), paginated() - 통일된 응답 구조"],
        ["오류 처리","app/common/exceptions.py","NotFoundError, MESException, HTTP 예외 핸들러"],
        ["페이지네이션","app/common/pagination.py","page/limit/offset 파라미터 처리"],
        ["S3 업로드","app/common/s3.py","AWS S3 파일 업로드, Presigned URL 생성"],
        ["JWT 인증","app/auth/service.py","토큰 생성/검증, 비밀번호 해시"],
    ])
doc.save(f"{OUT}/SF-TD4_프로그램설계서.docx")
print("[OK] SF-TD4_프로그램설계서.docx")


# ─────────────────── SF-TD5 데이터베이스설계서 ───────────────────────────
doc = new_doc(); cover(doc, "데이터베이스설계서", "SF-TD5"); history(doc)

doc.add_heading("1. DB 개요", level=1)
add_table(doc, ["항목","내용"],
    [
        ["DBMS","PostgreSQL 17 (AWS RDS)"],
        ["Extension","pgvector 0.3 (벡터 임베딩), uuid-ossp (UUID 생성)"],
        ["문자셋","UTF-8"],
        ["콜레이션","ko_KR.UTF-8"],
        ["연결방식","비동기 (asyncpg), 동기 (pg8000)"],
        ["백업","일일 자동 스냅샷 (AWS RDS), 7일 보관"],
    ])

doc.add_heading("2. 전체 테이블 목록 (35개)", level=1)
add_table(doc, ["No","테이블명","한글명","도메인","예상 레코드"],
    [
        ["1","users","사용자","시스템","100"],
        ["2","customer","고객사","수주","500"],
        ["3","order","수주","수주","10,000"],
        ["4","quote","견적","수주","10,000"],
        ["5","bom","BOM","수주","10,000"],
        ["6","bom_line","BOM 라인","수주","50,000"],
        ["7","cad_drawing","CAD 도면","CAD","5,000"],
        ["8","supplier","공급처","입고","100"],
        ["9","material","원자재","입고","500"],
        ["10","receiving_lot","입고 LOT","입고","50,000"],
        ["11","inventory_stock","재고 현황","입고","500"],
        ["12","material_allocation","자재 배정","입고","50,000"],
        ["13","work_order","작업지시","생산","10,000"],
        ["14","production_lot","생산 LOT","생산","50,000"],
        ["15","forming_process","성형 공정","생산","100,000"],
        ["16","welding_process","용접 공정","생산","100,000"],
        ["17","packing_record","포장 기록","생산","50,000"],
        ["18","plc_controller","PLC 컨트롤러","설비","10"],
        ["19","equipment","설비","설비","50"],
        ["20","equipment_sensor_data","설비 센서 데이터","설비","10,000,000"],
        ["21","quality_standard","품질 기준","품질","50"],
        ["22","quality_inspection","품질 검사","품질","100,000"],
        ["23","defect_record","불량 기록","품질","10,000"],
        ["24","shipping_order","출하 지시","출하","10,000"],
        ["25","shipping_lot","출하 LOT","출하","30,000"],
        ["26","claim","클레임","출하","1,000"],
        ["27","ai_agent_query","AI 질의 이력","AI","100,000"],
        ["28","knowledge_base","지식 베이스","AI","10,000"],
        ["29","kpi_record","KPI 기록","AI","1,000,000"],
        ["30","work_standard","작업 표준","기준정보","100"],
        ["31","code_master","코드 마스터","기준정보","1,000"],
        ["32","system_log","시스템 로그","시스템","1,000,000"],
        ["33","alert","알림","시스템","100,000"],
        ["34","routing","공정 순서","생산","100"],
        ["35","bom_routing_map","BOM-공정 매핑","생산","50,000"],
    ])

doc.add_heading("3. 주요 테이블 상세 (핵심 5개)", level=1)
doc.add_heading("3.1 order (수주)", level=2)
add_table(doc, ["컬럼명","타입","PK/FK","NOT NULL","기본값","설명"],
    [
        ["order_id","UUID","PK","Y","uuid4()","수주 ID"],
        ["order_no","VARCHAR(30)","","Y","","수주번호 (ORD-YYYY-NNNNNN)"],
        ["customer_id","UUID","FK(customer)","Y","","고객사 ID"],
        ["status","VARCHAR(20)","","Y","RECEIVED","RECEIVED/QUOTING/CONFIRMED/IN_PROGRESS/SHIPPED"],
        ["product_type","VARCHAR(50)","","Y","","LADDER_TRAY/CABLE_TRAY"],
        ["product_spec","JSONB","","Y","","제품 사양 (width_mm, thickness_mm, length_mm 등)"],
        ["quantity","INTEGER","","Y","","수주 수량"],
        ["requested_delivery_date","DATE","","N","","요청 납기일"],
        ["cad_drawing_id","UUID","FK(cad_drawing)","N","","연결된 CAD 도면"],
        ["is_deleted","BOOLEAN","","Y","false","소프트 삭제"],
        ["created_at","TIMESTAMPTZ","","Y","now()","생성일시"],
    ])

doc.add_heading("3.2 equipment_sensor_data (설비 센서 — TimescaleDB Hypertable)", level=2)
add_table(doc, ["컬럼명","타입","인덱스","설명"],
    [
        ["sensor_record_id","UUID","PK","레코드 ID"],
        ["equipment_id","UUID","FK+IDX","설비 ID"],
        ["timestamp","TIMESTAMPTZ","IDX (파티션 키)","측정 시각"],
        ["pressure_mpa","NUMERIC(8,3)","","압력 (MPa)"],
        ["speed_mpm","NUMERIC(8,3)","","속도 (m/min)"],
        ["current_a","NUMERIC(8,3)","","전류 (A)"],
        ["voltage_v","NUMERIC(8,3)","","전압 (V)"],
        ["temperature_c","NUMERIC(6,2)","","온도 (℃)"],
        ["anomaly_flag","BOOLEAN","IDX","이상 감지 여부"],
        ["sensor_snapshot","JSONB","","전체 센서 스냅샷"],
    ])

doc.add_heading("4. 인덱스 설계", level=1)
add_table(doc, ["테이블","인덱스명","컬럼","유형","목적"],
    [
        ["order","idx_order_status","status","B-Tree","상태별 필터링"],
        ["order","idx_order_customer","customer_id","B-Tree","고객사별 조회"],
        ["receiving_lot","idx_lot_material","material_code","B-Tree","자재별 LOT 조회"],
        ["equipment_sensor_data","idx_sensor_equipment_time","(equipment_id, timestamp)","B-Tree","시계열 범위 조회"],
        ["knowledge_base","idx_kb_embedding","embedding","IVFFLAT (pgvector)","유사도 벡터 검색"],
        ["quality_inspection","idx_qi_lot","production_lot_id","B-Tree","LOT별 검사 조회"],
    ])
doc.save(f"{OUT}/SF-TD5_데이터베이스설계서.docx")
print("[OK] SF-TD5_데이터베이스설계서.docx")

print("\n설계단계 5개 완료!")
