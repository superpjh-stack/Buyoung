"""분석단계 3개 산출물 생성 SF-AD1, SF-AD2, SF-AD3"""
import os, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

OUT = os.path.dirname(os.path.abspath(__file__))
BLUE = RGBColor(0, 70, 127)


def cover(doc, title, doc_no):
    for _ in range(4):
        doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(title)
    r.font.size = Pt(24); r.font.bold = True; r.font.color.rgb = BLUE
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
        for ci, val in enumerate(row):
            t.rows[ri+1].cells[ci].text = str(val)
    doc.add_paragraph()


# ─────────────────── SF-AD1 현행업무분석서 ───────────────────────────────
doc = Document()
s = doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
for m in ("top","bottom","left","right"): setattr(s, m+"_margin", Cm(2.5))
cover(doc, "현행업무분석서", "SF-AD1"); history(doc)

doc.add_heading("1. 사업 개요", level=1)
for txt in [
    "사업명: 주식회사 부영기업 제조AI 특화 스마트공장 MES 구축 사업",
    "사업기간: 2026년 6월 ~ 2026년 11월 (6개월)",
    "사업목적: 래더트레이/케이블트레이 제조 공정에 AI 기술 적용으로 스마트공장 구현",
    "도입기업: 주식회사 부영기업 (경기도 소재, 금속 판금 제조업)",
]: doc.add_paragraph(txt, style="List Bullet")

doc.add_heading("2. 현행 업무 현황", level=1)
doc.add_paragraph("현재 업무는 수기 및 엑셀 기반으로 운영되며 7개 주요 공정으로 구성됩니다.")
add_table(doc,
    ["공정","업무내용","담당자","현행도구","주요문제"],
    [
        ["수주접수","고객 견적 요청 수신 및 접수","영업팀","이메일/전화/엑셀","견적 처리 지연(2~3일)"],
        ["CAD 분석","도면 수동 검토 및 치수 측정","설계팀","AutoCAD","분석 시간 과다, 오류 발생"],
        ["견적 산출","수동 원가 계산 및 견적서 작성","견적팀","엑셀","산출 오류, 일관성 결여"],
        ["BOM 작성","자재 소요량 수동 산출","생산기술팀","엑셀","누락 위험, 버전 관리 불가"],
        ["생산 관리","공정 실적 수기 기록","생산팀","종이/엑셀","실시간 파악 불가"],
        ["품질 검사","검사 결과 수기 기록 및 관리","품질팀","종이 대장","LOT 이력 추적 어려움"],
        ["출하 관리","출하 서류 수동 작성 및 관리","물류팀","엑셀","납기 대응 지연"],
    ])

doc.add_heading("3. 현행 시스템 현황", level=1)
for txt in [
    "주요 사용 시스템: MS Office(Excel, Word), AutoCAD 2023",
    "데이터 저장: 공유 폴더 + 개인 PC (버전 관리 불가)",
    "시스템 간 연계: 없음 (각 공정 완전 수작업 처리)",
    "사용자 수: 약 20명 (영업, 설계, 생산, 품질, 물류)",
]: doc.add_paragraph(txt, style="List Bullet")
add_table(doc,
    ["시스템","용도","사용부서","문제점"],
    [
        ["MS Excel","견적/BOM/생산실적/출하 관리","전 부서","수작업 오류, 실시간성 없음"],
        ["AutoCAD 2023","도면 작성 및 검토","설계팀","수동 분석, AI 미활용"],
        ["이메일","고객 주문 접수","영업팀","체계적 관리 불가"],
    ])

doc.add_heading("4. 현행 업무 문제점 및 개선 필요성", level=1)
add_table(doc,
    ["문제점","영향","개선 방향","기대효과"],
    [
        ["수동 견적 산출 (2~3일 소요)","고객 응대 지연, 기회 손실","AI 자동 견적(XGBoost)","견적 시간 94% 단축"],
        ["CAD 도면 수동 분석","설계 오류, 견적 부정확","AI 도면 파싱(YOLOv8)","정확도 95% 향상"],
        ["LOT 추적 불가","품질 문제 원인 추적 어려움","Digital Thread 구현","전 공정 이력 추적"],
        ["실시간 생산현황 미파악","납기 관리 어려움","IoT 데이터 실시간 수집","납기 준수율 20%p 향상"],
        ["수기 품질 기록","불량 원인 분석 어려움","시스템 기반 품질 관리","불량률 60% 감소"],
    ])

doc.save(f"{OUT}/SF-AD1_현행업무분석서.docx")
print("[OK] SF-AD1_현행업무분석서.docx")


# ─────────────────── SF-AD2 요구사항정의서 ───────────────────────────────
doc = Document()
s = doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
for m in ("top","bottom","left","right"): setattr(s, m+"_margin", Cm(2.5))
cover(doc, "요구사항정의서", "SF-AD2"); history(doc)

doc.add_heading("1. 기능 요구사항", level=1)
doc.add_paragraph("총 30개 기능 요구사항 / 우선순위: 필수(M)/권장(S)/선택(W)")
add_table(doc,
    ["요구사항ID","기능명","상세내용","우선순위"],
    [
        ["FR-001","CAD 도면 자동 파싱","DWG/PDF 도면에서 객체·치수·형상 자동 추출","M"],
        ["FR-002","자동 견적 산출","XGBoost 기반 공정별 원가 및 총 견적 자동 계산","M"],
        ["FR-003","BOM 자동 생성","GNN 기반 도면 객체 관계로 자재·공정 구조 자동 생성","M"],
        ["FR-004","RAG AI Agent","자연어 질의응답 (전 공정 데이터 조회)","M"],
        ["FR-005","AI KPI 대시보드","실시간 생산·품질·설비·출하 KPI 시각화","M"],
        ["FR-006","입고 LOT 관리","원자재 입고 시 LOT/규격/중량 등록 및 이력 관리","M"],
        ["FR-007","공급처 품질 분석","공급처별 불량률·납품 이력 분석","M"],
        ["FR-008","원자재 이력 조회","LOT 기준 입고→사용→출하 전 과정 이력 추적","M"],
        ["FR-009","재고 현황 관리","자재별 보유/할당/가용 재고 실시간 관리","M"],
        ["FR-010","입고 AI Agent","RAG 기반 입고 품질 판단 지원","S"],
        ["FR-011","작업지시 관리","수주 기반 작업지시 생성 및 상태 관리","M"],
        ["FR-012","생산 LOT 관리","공정별 생산 LOT 실적 수집 및 관리","M"],
        ["FR-013","공정 데이터 모니터링","속도·압력·온도 공정 데이터 실시간 수집","M"],
        ["FR-014","공정 이력 조회","LOT 기준 공정 진행 이력 조회","M"],
        ["FR-015","공정 데이터 분석","수율·불량률·병목 원인 분석","S"],
        ["FR-016","품질 검사 관리","공정별 품질 검사 결과 등록 및 조회","M"],
        ["FR-017","불량 기록 관리","불량 유형·위치·심각도·조치 기록","M"],
        ["FR-018","품질 기준 관리","제품·공정별 품질 기준 정의 및 관리","M"],
        ["FR-019","품질 KPI 조회","불량률·합격률·클레임 발생률 산출","M"],
        ["FR-020","출하 관리","출하 지시·LOT 배정·출하 확정 관리","M"],
        ["FR-021","LOT 추적 관리","제품 LOT 기준 전 공정 이력 추적","M"],
        ["FR-022","클레임 관리","고객 클레임 접수·조사·종결 관리","M"],
        ["FR-023","출하 AI Agent","출하 가능 여부 및 리스크 대응 가이드","S"],
        ["FR-024","설비 상태 모니터링","설비 가동률·이상 감지·OEE 계산","M"],
        ["FR-025","센서 데이터 수집","IoT 센서 데이터 실시간 수집 (TimescaleDB)","M"],
        ["FR-026","KPI 목표 관리","KPI 목표값 설정 및 달성률 분석","M"],
        ["FR-027","사용자 관리","사용자 계정·역할·권한 관리","M"],
        ["FR-028","데이터 시각화","대시보드·그래프·추이 분석 화면","M"],
        ["FR-029","데이터 다운로드","분석 데이터 CSV/Excel 내보내기","S"],
        ["FR-030","AI 학습 데이터 관리","ML 모델 학습용 데이터셋 관리","W"],
    ])

doc.add_heading("2. 비기능 요구사항", level=1)
add_table(doc,
    ["요구사항ID","유형","요구사항명","기준"],
    [
        ["NFR-001","성능","응답시간","일반 조회 200ms 이내, AI 질의 3초 이내"],
        ["NFR-002","가용성","시스템 가용성","99.5% 이상"],
        ["NFR-003","확장성","동시 사용자","최대 100명 동시 접속 지원"],
        ["NFR-004","보안","통신 보안","HTTPS 필수, TLS 1.3 이상"],
        ["NFR-005","보안","인증/인가","JWT 기반 인증, RBAC 역할 기반 접근 제어"],
        ["NFR-006","보안","데이터 보호","개인정보보호법 준수, bcrypt 암호화"],
        ["NFR-007","유지보수","로그 관리","시스템 로그 90일 보관"],
        ["NFR-008","사용성","UI 반응성","Chrome/Edge 최신, 해상도 1280x720 이상"],
        ["NFR-009","호환성","API 표준","REST API, JSON, OpenAPI 3.0 문서화"],
        ["NFR-010","재해복구","DB 백업","일일 자동 백업, RTO 4시간 이내"],
    ])

doc.add_heading("3. 제약사항 및 가정", level=1)
for txt in [
    "기술 제약: Python 3.13+, PostgreSQL 17+, Node.js 22+, Next.js 16+",
    "환경 제약: AWS 클라우드 환경 (ap-northeast-2 리전)",
    "법적 제약: 개인정보보호법, 정보통신망법 준수",
    "일정 제약: 사업 기간 6개월 내 전체 기능 구현 완료",
]: doc.add_paragraph(txt, style="List Bullet")

doc.add_heading("4. 요구사항 우선순위", level=1)
add_table(doc,
    ["우선순위","요구사항 ID 목록","개수"],
    [
        ["필수(M)","FR-001~009, FR-011~014, FR-016~022, FR-024~028","24개"],
        ["권장(S)","FR-010, FR-015, FR-023, FR-029","4개"],
        ["선택(W)","FR-030","1개(예산 내 구현 검토)"],
    ])

doc.save(f"{OUT}/SF-AD2_요구사항정의서.docx")
print("[OK] SF-AD2_요구사항정의서.docx")


# ─────────────────── SF-AD3 기능대비표 ───────────────────────────────────
doc = Document()
s = doc.sections[0]; s.page_width=Cm(21); s.page_height=Cm(29.7)
for m in ("top","bottom","left","right"): setattr(s, m+"_margin", Cm(2.5))
cover(doc, "기능대비표", "SF-AD3"); history(doc)

doc.add_heading("1. 기능 대비표", level=1)
doc.add_paragraph("솔루션 고유 기능을 기존활용/추가/변경/삭제로 구분합니다.")
add_table(doc,
    ["기능명","구분","AS-IS","TO-BE","관련 요구사항"],
    [
        ["AI 대시보드 (KPI)","추가","없음","실시간 4개 KPI 카드","FR-005"],
        ["CAD 도면 AI 파싱","추가","수동 AutoCAD","YOLOv8 자동 파싱","FR-001"],
        ["자동 견적 산출","추가","엑셀 수동 계산","XGBoost 자동 산출","FR-002"],
        ["SHAP 영향요인 분석","추가","없음","SHAP 기반 변수 분석","FR-002"],
        ["BOM 자동 생성","추가","수동 작성","GNN 자동 생성","FR-003"],
        ["RAG AI Agent","추가","없음","LangChain+pgvector","FR-004"],
        ["수주 관리","변경","이메일+엑셀","시스템 기반 관리","FR-001~003"],
        ["견적 승인/거절","추가","구두/이메일","API 기반 승인 플로우","FR-002"],
        ["입고 LOT 관리","추가","수기 대장","LOT 기반 시스템 관리","FR-006"],
        ["원자재 이력 조회","추가","없음","Digital Thread 추적","FR-008"],
        ["공급처 품질 분석","추가","없음","불량률·이력 분석","FR-007"],
        ["재고 현황 관리","추가","엑셀","실시간 재고 관리","FR-009"],
        ["작업지시 관리","추가","구두 지시","시스템 작업지시","FR-011"],
        ["생산 LOT 추적","추가","수기","실시간 LOT 관리","FR-012"],
        ["공정 데이터 모니터링","추가","없음","IoT 실시간 수집","FR-013"],
        ["품질 검사 관리","변경","수기 대장","시스템 기반 관리","FR-016,017"],
        ["출하 관리","변경","엑셀","시스템 기반 출하","FR-020"],
        ["LOT 추적 관리","추가","없음","전 공정 Digital Thread","FR-021"],
        ["클레임 관리","추가","수기","시스템 클레임 관리","FR-022"],
        ["설비 IoT 모니터링","추가","없음","OPC-UA/Modbus 연계","FR-024,025"],
        ["KPI 목표 관리","추가","없음","KPI 목표/실적 관리","FR-026"],
        ["사용자 권한 관리","추가","없음","RBAC 역할 기반","NFR-005"],
        ["WebSocket 실시간","추가","없음","KPI/설비 실시간 스트림","NFR-001"],
    ])

doc.add_heading("2. 추가 기능 상세", level=1)
for txt in [
    "CAD AI 파싱: Autodesk APS + YOLOv8을 활용한 DWG/PDF 도면 자동 분석 (치수·형상·부품 추출)",
    "XGBoost 견적: 공정 데이터 기반 원가 예측 모델 (SHAP 설명 가능성 포함, R2 > 0.90)",
    "RAG Agent: LangChain + pgvector 기반 자연어 질의응답 시스템 (전 공정 데이터 조회)",
    "GNN BOM: 도면 객체 그래프 관계 기반 자재·공정 구조 자동 생성",
    "Digital Thread: 수주→입고→생산→품질→출하 전 과정 LOT 기준 이력 연계",
]: doc.add_paragraph(txt, style="List Bullet")

doc.add_heading("3. 기능 구현 근거", level=1)
doc.add_paragraph(
    "본 기능대비표는 사업계획서 3.1 솔루션 기능 구성도(p.40) 및 요구사항정의서(SF-AD2)를 "
    "기준으로 작성되었으며, 추가·변경 기능은 FP 산출 기준에 포함됩니다.")

doc.save(f"{OUT}/SF-AD3_기능대비표.docx")
print("[OK] SF-AD3_기능대비표.docx")
print("\n분석단계 3개 완료!")
