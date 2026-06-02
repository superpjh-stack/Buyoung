# -*- coding: utf-8 -*-
"""
부영기업 AI MES 프로젝트 — 분석단계 문서 생성 스크립트
SF-AD1 현행업무분석서 / SF-AD2 요구사항정의서 / SF-AD3 기능대비표
"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy
from datetime import date
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────
# 공통 스타일 유틸리티
# ─────────────────────────────────────────────

COLOR_HEADER_BG  = "1F3864"   # 진한 남색 (표 헤더)
COLOR_HEADER2_BG = "2E75B6"   # 중간 파란색 (섹션 헤더)
COLOR_ACCENT_BG  = "D6E4F0"   # 연한 파란색 (강조 행)
COLOR_WHITE      = "FFFFFF"
COLOR_DARK_TEXT  = "1A1A1A"
COLOR_SUBHEADER  = "2F5496"


def set_cell_bg(cell, hex_color: str):
    """셀 배경색 설정."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement("w:shd")
    shd.set(qn("w:val"),   "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"),  hex_color)
    tcPr.append(shd)


def set_cell_border(cell, border_color="AAAAAA", border_sz="4"):
    """셀 테두리 설정."""
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        side = OxmlElement(f"w:{edge}")
        side.set(qn("w:val"),   "single")
        side.set(qn("w:sz"),    border_sz)
        side.set(qn("w:space"), "0")
        side.set(qn("w:color"), border_color)
        tcBorders.append(side)
    tcPr.append(tcBorders)


def set_para_spacing(para, before=0, after=0, line=None):
    pPr  = para._p.get_or_add_pPr()
    spng = OxmlElement("w:spacing")
    spng.set(qn("w:before"), str(before))
    spng.set(qn("w:after"),  str(after))
    if line:
        spng.set(qn("w:line"),     str(line))
        spng.set(qn("w:lineRule"), "auto")
    pPr.append(spng)


def add_heading(doc: Document, text: str, level: int = 1):
    """스타일 있는 제목 추가."""
    para = doc.add_paragraph()
    run  = para.add_run(text)
    if level == 1:
        run.font.size  = Pt(16)
        run.font.bold  = True
        run.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
        para.paragraph_format.space_before = Pt(18)
        para.paragraph_format.space_after  = Pt(6)
    elif level == 2:
        run.font.size  = Pt(13)
        run.font.bold  = True
        run.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)
        para.paragraph_format.space_before = Pt(12)
        para.paragraph_format.space_after  = Pt(4)
    elif level == 3:
        run.font.size  = Pt(11)
        run.font.bold  = True
        run.font.color.rgb = RGBColor(0x2F, 0x54, 0x96)
        para.paragraph_format.space_before = Pt(8)
        para.paragraph_format.space_after  = Pt(2)
    para.paragraph_format.keep_with_next = True
    return para


def add_body(doc: Document, text: str, bullet: bool = False):
    para = doc.add_paragraph()
    if bullet:
        para.style = doc.styles["List Bullet"] if "List Bullet" in [s.name for s in doc.styles] else doc.styles["Normal"]
        run = para.add_run(f"• {text}")
    else:
        run = para.add_run(text)
    run.font.size = Pt(10)
    run.font.name = "맑은 고딕"
    para.paragraph_format.space_after = Pt(2)
    return para


def styled_table(doc: Document, headers: list, rows: list,
                 col_widths: list = None) -> None:
    """헤더(진한 남색) + 데이터 행 표 추가."""
    n_cols = len(headers)
    table  = doc.add_table(rows=1 + len(rows), cols=n_cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # 헤더 행
    hdr_row = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr_row.cells[i]
        set_cell_bg(cell, COLOR_HEADER_BG)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p    = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run  = p.add_run(h)
        run.font.bold  = True
        run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        run.font.size  = Pt(9)
        run.font.name  = "맑은 고딕"

    # 데이터 행
    for r_idx, row_data in enumerate(rows):
        tr   = table.rows[r_idx + 1]
        bg   = COLOR_ACCENT_BG if r_idx % 2 == 0 else COLOR_WHITE
        for c_idx, val in enumerate(row_data):
            cell = tr.cells[c_idx]
            set_cell_bg(cell, bg)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p   = cell.paragraphs[0]
            run = p.add_run(str(val))
            run.font.size = Pt(9)
            run.font.name = "맑은 고딕"

    # 열 너비
    if col_widths:
        for row in table.rows:
            for i, w in enumerate(col_widths):
                row.cells[i].width = Cm(w)

    doc.add_paragraph()  # 표 아래 여백


def add_cover(doc: Document, doc_no: str, title: str, subtitle: str):
    """표지 페이지 추가."""
    # 상단 여백
    for _ in range(4):
        doc.add_paragraph()

    # 문서번호
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"문서번호: {doc_no}")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(0x88, 0x88, 0x88)

    doc.add_paragraph()

    # 메인 타이틀
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(title)
    run.font.size  = Pt(28)
    run.font.bold  = True
    run.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)

    doc.add_paragraph()

    # 서브타이틀
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(subtitle)
    run.font.size  = Pt(14)
    run.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)

    for _ in range(2):
        doc.add_paragraph()

    # 구분선
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("─" * 40)
    run.font.color.rgb = RGBColor(0x2E, 0x75, 0xB6)

    for _ in range(3):
        doc.add_paragraph()

    # 발행 정보 표
    info_table = doc.add_table(rows=5, cols=2)
    info_table.style = "Table Grid"
    info_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta = [
        ("과제명",    "제조AI특화 스마트공장 구축지원사업"),
        ("도입기업",  "주식회사 부영기업"),
        ("공급기업",  "㈜아이시프트"),
        ("작성일",    date.today().strftime("%Y년 %m월 %d일")),
        ("버전",      "v1.0"),
    ]
    for i, (k, v) in enumerate(meta):
        lc = info_table.rows[i].cells[0]
        rc = info_table.rows[i].cells[1]
        set_cell_bg(lc, COLOR_HEADER2_BG)
        lc.width = Cm(4)
        rc.width = Cm(10)
        lp = lc.paragraphs[0]
        lp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        lr = lp.add_run(k)
        lr.font.bold  = True
        lr.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        lr.font.size  = Pt(10)
        rp = rc.paragraphs[0]
        rr = rp.add_run(v)
        rr.font.size = Pt(10)

    doc.add_page_break()


def add_toc_page(doc: Document, entries: list):
    """목차 페이지 추가. entries = [(번호, 제목, 페이지), ...]"""
    add_heading(doc, "목  차", 1)
    doc.add_paragraph()
    for no, title, pg in entries:
        p   = doc.add_paragraph()
        run = p.add_run(f"{no}  {title}")
        run.font.size = Pt(10)
        run.font.name = "맑은 고딕"
        tab = p.add_run(f"{'.' * max(1, 60 - len(no) - len(title))} {pg}")
        tab.font.size  = Pt(10)
        tab.font.color.rgb = RGBColor(0x88, 0x88, 0x88)
    doc.add_page_break()


# ─────────────────────────────────────────────
# SF-AD1  현행업무분석서
# ─────────────────────────────────────────────

def build_sf_ad1():
    doc = Document()

    # 여백 설정
    for section in doc.sections:
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin   = Cm(3.0)
        section.right_margin  = Cm(2.5)

    # ── 표지
    add_cover(doc,
              "SF-AD1-001",
              "현행업무분석서",
              "AS-IS 업무 현황 및 문제점 분석")

    # ── 목차
    toc = [
        ("1.",   "문서 개요",                           "3"),
        ("1.1",  "분석 목적 및 범위",                   "3"),
        ("1.2",  "분석 방법론 및 일정",                 "3"),
        ("1.3",  "참여 인원",                           "4"),
        ("2.",   "기업 현황",                           "4"),
        ("2.1",  "기업 일반 현황",                      "4"),
        ("2.2",  "생산 제품 현황",                      "5"),
        ("2.3",  "조직 구조",                           "5"),
        ("3.",   "현행 업무 프로세스 분석 (AS-IS)",     "6"),
        ("3.1",  "수주·견적 업무",                      "6"),
        ("3.2",  "입고·재고 업무",                      "7"),
        ("3.3",  "생산 공정 업무 (포밍·용접·포장)",     "8"),
        ("3.4",  "출하·물류 업무",                      "9"),
        ("4.",   "현행 시스템 현황",                    "10"),
        ("4.1",  "시스템 현황 개요",                    "10"),
        ("4.2",  "시스템별 상세 현황",                  "10"),
        ("4.3",  "데이터 관리 현황",                    "11"),
        ("5.",   "문제점 및 개선 요구사항 도출",        "12"),
        ("5.1",  "공정별 핵심 문제 요약",               "12"),
        ("5.2",  "데이터 구조 문제",                    "13"),
        ("5.3",  "개선 방향",                           "13"),
        ("[별첨]", "인터뷰 결과 요약",                  "14"),
    ]
    add_toc_page(doc, toc)

    # ══════════════════════════════════════════
    # 섹션 1. 문서 개요
    # ══════════════════════════════════════════
    add_heading(doc, "1. 문서 개요", 1)

    add_heading(doc, "1.1 분석 목적 및 범위", 2)
    add_body(doc, "본 문서는 주식회사 부영기업의 제조AI 스마트공장 구축 프로젝트(과제번호: SF26179181)를 위해 "
                  "현행(AS-IS) 업무 프로세스, 시스템 현황, 데이터 관리 체계를 분석하고 문제점을 도출하는 것을 "
                  "목적으로 한다.")
    add_body(doc, "")
    add_body(doc, "분석 범위는 수주·견적 → 원자재 입고/보관 → 포밍 → 용접 → 포장 → 보관/출하에 이르는 "
                  "전(全) 제조 공정과 이를 지원하는 IT 시스템을 포함한다.")

    styled_table(doc,
        ["분석 영역", "세부 범위", "비고"],
        [
            ["업무 프로세스", "수주·견적, 입고·재고, 포밍, 용접, 포장, 출하 6개 공정", "전 공정"],
            ["IT 시스템",     "ERP, CAD 시스템, Excel 관리 체계",                       "현행 시스템"],
            ["데이터 관리",   "공정 데이터, 품질 데이터, 이력 관리 체계",               "AS-IS 데이터"],
            ["조직·인력",     "공정별 담당자, 역할, 업무 분장",                          "19명 규모"],
        ],
        col_widths=[3.5, 9.0, 3.5]
    )

    add_heading(doc, "1.2 분석 방법론 및 일정", 2)
    add_body(doc, "현행업무 분석은 현장 인터뷰, 업무 관찰, 문서 검토의 3가지 방법을 병행하여 수행한다.")

    styled_table(doc,
        ["분석 방법", "내용", "기간"],
        [
            ["현장 인터뷰",  "공정별 담당자 인터뷰 (수주·견적 2회, 생산 2회, 출하 1회)", "2026년 7월 1주~2주"],
            ["업무 관찰",    "현장 직접 관찰 및 프로세스 플로우 확인",                   "2026년 7월 2주~3주"],
            ["문서 검토",    "기존 Excel 양식, ERP 화면, 작업표준서, 견적 기준서 검토",  "2026년 7월 3주~4주"],
            ["분석 정리",    "인터뷰 결과 종합, 문제점 도출, 문서 작성",                 "2026년 8월 1주"],
        ],
        col_widths=[3.5, 9.0, 3.5]
    )

    add_heading(doc, "1.3 참여 인원", 2)
    styled_table(doc,
        ["구분", "소속", "성명", "역할"],
        [
            ["도입기업", "부영기업 생산팀",    "담당자 A", "생산·공정 현황 인터뷰 응답"],
            ["도입기업", "부영기업 품질팀",    "담당자 B", "품질·출하 현황 인터뷰 응답"],
            ["도입기업", "부영기업 영업팀",    "담당자 C", "수주·견적 현황 인터뷰 응답"],
            ["공급기업", "㈜아이시프트 PM",    "PM",       "전체 분석 총괄"],
            ["공급기업", "㈜아이시프트 분석팀", "분석가",  "현행업무 분석 수행"],
        ],
        col_widths=[2.5, 4.0, 3.0, 6.5]
    )

    # ══════════════════════════════════════════
    # 섹션 2. 기업 현황
    # ══════════════════════════════════════════
    add_heading(doc, "2. 기업 현황", 1)

    add_heading(doc, "2.1 기업 일반 현황", 2)
    styled_table(doc,
        ["항목", "내용"],
        [
            ["기업명",    "주식회사 부영기업"],
            ["설립연도",  "2012년 (전신: 대광볼트(주) 1987년 설립)"],
            ["대표자",    "이영화"],
            ["소재지",    "경기도 화성시 송산면 송산로152번길 4-25"],
            ["업종",      "금속 압형제품 제조업"],
            ["종업원 수", "19명"],
            ["주요 인증", "ISO 9001(품질), ISO 14001(환경), ISO 45001(안전), KS 인증"],
            ["주요 특허", "내진형 케이블트레이 등 다수의 특허·실용신안·디자인권 보유"],
            ["매출 현황", "2022년 57억 / 2023년 56억 / 2024년 52억 원"],
        ],
        col_widths=[4.0, 12.0]
    )

    add_heading(doc, "2.2 생산 제품 현황", 2)
    styled_table(doc,
        ["제품군", "주요 제품", "특징"],
        [
            ["케이블 지지 구조재", "Cable Tray",         "표준형, 내진형, 방청형 등 다양한 규격"],
            ["케이블 지지 구조재", "Ladder Tray",        "대용량 케이블 포설용, KS 규격 준수"],
            ["케이블 지지 구조재", "Solid Bottom Tray",  "밀폐형, 방수·방진 요구 환경 적용"],
            ["부속 자재",          "연결재, 지지대, 볼트/너트", "구조재와 함께 공급되는 부속품 일체"],
        ],
        col_widths=[4.0, 4.0, 8.0]
    )

    add_heading(doc, "2.3 조직 구조 및 공정 흐름", 2)
    add_body(doc, "부영기업은 19명 규모의 중소 제조기업으로, 영업/견적, 생산, 품질, 물류 기능이 소수 인원에 "
                  "의해 운영된다. 생산 공정은 아래 순서로 진행된다.")

    styled_table(doc,
        ["단계", "공정명", "주요 활동", "담당"],
        [
            ["1", "수주·견적",       "CAD 도면 수신, 수작업 견적 산출, 수주 확정",  "영업/견적 담당"],
            ["2", "원자재 입고/보관", "자재 입고 검사, 창고 보관, 재고 관리",        "자재 담당"],
            ["3", "포밍(절곡)",      "코일 투입→피딩→타공→성형 연속 공정",          "생산 담당"],
            ["4", "용접",            "로봇/수작업 용접, 완료 수기 기록",             "용접 담당"],
            ["5", "포장",            "검사 후 포장, 수량 수기 집계",                 "생산 담당"],
            ["6", "보관/출하",       "LOT 관리, 출하 지시, 납기 확인",              "물류 담당"],
        ],
        col_widths=[1.5, 3.5, 7.5, 3.5]
    )

    # ══════════════════════════════════════════
    # 섹션 3. 현행 업무 프로세스 분석
    # ══════════════════════════════════════════
    add_heading(doc, "3. 현행 업무 프로세스 분석 (AS-IS)", 1)

    add_heading(doc, "3.1 수주·견적 업무", 2)
    add_body(doc, "현행 수주·견적 프로세스는 영업 담당자가 CAD 도면(DWG/PDF)을 수신하여 수작업으로 자재·공정·공수를 "
                  "산정하는 방식으로 운영된다. 평균 견적 리드타임은 1일 이상 소요된다.")

    styled_table(doc,
        ["프로세스 단계", "현행 방법", "문제점", "영향"],
        [
            ["도면 수신",    "고객 이메일·팩스로 CAD 파일 수신",    "파일 버전 관리 체계 없음",              "도면 오류 위험"],
            ["도면 해석",    "작업자 수작업 해석 (Autodesk 뷰어)",  "담당자 역량에 따른 결과 편차",          "견적 오차 ±10%"],
            ["자재 산출",    "경험 기반 수량 산정, Excel 입력",     "과거 견적 데이터와 미연계",             "반복 업무 비효율"],
            ["공정·공수 산출", "공수표 참조, 수동 계산",            "표준 원가 기준 미정립",                 "원가 오류 발생"],
            ["견적서 작성",  "Excel 견적서 수기 작성",              "BOM-공정-원가 통합 데이터 없음",        "리드타임 1일 이상"],
            ["수주 확정",    "구두/이메일 수주 확정, ERP 입력",     "ERP와 CAD 데이터 연계 없음",            "디지털 연계 단절"],
        ],
        col_widths=[3.5, 4.5, 4.5, 3.5]
    )

    add_heading(doc, "3.2 입고·재고 업무", 2)
    add_body(doc, "원자재 입고 시 수기 검사 및 Excel 입력으로 관리되며, 실시간 재고 가시성이 부족하다.")

    styled_table(doc,
        ["프로세스 단계", "현행 방법", "문제점", "영향"],
        [
            ["입고 수신",     "거래명세서 기반 수기 수량 확인",          "전산 실시간 미반영",               "재고 오차 상시 존재"],
            ["입고 검사",     "육안 검사, 수기 기록",                    "검사 기준서 미표준화",             "불량 자재 입고 위험"],
            ["LOT 관리",      "LOT 번호 수기 부착, Excel 기록",          "공정 데이터와 LOT 미연계",         "추적 불가"],
            ["재고 위치 관리", "작업자 경험 기반 위치 지정",             "위치 정보 전산화 없음",            "자재 부족/과잉 발생"],
            ["재고 현황 파악", "Excel 집계 (일 1회 수동 갱신)",          "실시간 가시성 없음",               "의사결정 지연"],
        ],
        col_widths=[3.5, 4.5, 4.5, 3.5]
    )

    add_heading(doc, "3.3 생산 공정 업무 (포밍·용접·포장)", 2)

    styled_table(doc,
        ["공정", "현행 방법", "주요 문제점", "영향"],
        [
            ["포밍",  "속도·압력·금형 조건 수동 설정 (경험 기반)",  "공정 조건 데이터 미수집",    "품질 편차 반복, 원인 분석 불가"],
            ["포밍",  "실시간 설비 모니터링 없음",                  "설비 이상 조기 감지 불가",   "초기 불량 지속 발생"],
            ["용접",  "로봇/수작업 용접 완료 수기·구두 보고",       "전류·전압·속도 등 미수집",   "불량 원인 공정 추적 불가"],
            ["용접",  "품질 데이터와 공정 데이터 미연계",           "LOT별 품질 추적 불가",       "클레임 대응 어려움"],
            ["포장",  "포장 수량·실적 수기 집계",                   "생산실적과 포장 수량 오차",  "출하 준비 비효율"],
        ],
        col_widths=[2.0, 5.0, 4.5, 4.5]
    )

    add_heading(doc, "3.4 출하·물류 업무", 2)

    styled_table(doc,
        ["프로세스 단계", "현행 방법", "문제점", "영향"],
        [
            ["출하 지시",   "수기/이메일 출하 지시",                  "출하 현황 실시간 파악 불가",      "납기 지연 위험"],
            ["LOT 추적",    "출하 이력 Excel 기록",                   "LOT-생산-출하 연계 없음",         "클레임 대응 장시간"],
            ["품질 검증",   "샘플 육안 검사",                          "불량 유출 가능성",               "고객 신뢰도 저하"],
            ["납기 관리",   "수기 납기 리스트 관리",                   "납기 지연 사전 감지 없음",       "긴급 대응 반복"],
            ["클레임 대응", "이력 수기 조회 (시간 소요)",              "원인 분석 데이터 미비",          "재발 방지 어려움"],
        ],
        col_widths=[3.5, 4.5, 4.5, 3.5]
    )

    # ══════════════════════════════════════════
    # 섹션 4. 현행 시스템 현황
    # ══════════════════════════════════════════
    add_heading(doc, "4. 현행 시스템 현황", 1)

    add_heading(doc, "4.1 시스템 현황 개요", 2)
    styled_table(doc,
        ["시스템", "도입 여부", "도입 시기", "현황"],
        [
            ["ERP",          "부분 도입", "2022년",  "자체 구축 (5백만원), 현장 데이터와 실시간 미연계"],
            ["MES",          "미도입",    "—",       "공정 실적 수기 기록, 작업지시 전산화 없음"],
            ["CAD 시스템",   "활용 중",   "기존",    "Autodesk 활용, 견적 AI 미적용, 수작업 해석"],
            ["IoT/PLC 연계", "미구축",    "—",       "포밍·용접 공정 데이터 수집 체계 없음"],
            ["재고·출하 관리", "Excel",   "기존",    "Excel + 수기 혼용, 실시간 연계 없음"],
            ["품질 관리 시스템", "미도입", "—",      "수기 검사 기록, LOT 추적 불가"],
        ],
        col_widths=[3.5, 2.5, 2.5, 7.5]
    )

    add_heading(doc, "4.2 ERP 시스템 상세 현황", 2)
    styled_table(doc,
        ["모듈", "활용 현황", "미활용 기능", "연계 한계"],
        [
            ["수주 관리",   "수주 입력, 고객 정보 관리",    "CAD 도면 연계",    "견적 데이터 미연계"],
            ["구매/자재",   "발주 입력, 거래처 관리",       "LOT 추적",         "입고 실시간 반영 없음"],
            ["생산 관리",   "작업지시 일부 입력",            "공정 실적 자동화", "현장 IoT 미연계"],
            ["회계/원가",   "세금계산서, 거래 기록",         "원가 분석",        "공정 원가 계산 불가"],
        ],
        col_widths=[3.0, 5.0, 4.5, 3.5]
    )

    add_heading(doc, "4.3 데이터 관리 현황", 2)
    add_body(doc, "현재 생산·품질·설비 데이터는 분산 관리되며, 공정 간 데이터 연결이 없는 상태이다.")

    styled_table(doc,
        ["데이터 유형", "현행 관리 방법", "보관 위치", "한계점"],
        [
            ["수주·견적 데이터",  "Excel 견적서, 이메일 보관",     "로컬 PC, 이메일",    "버전 관리 없음, 분실 위험"],
            ["자재 입고 데이터",  "Excel 입고대장, 수기 기록",     "사무실 파일 서버",   "실시간 반영 없음"],
            ["공정 데이터",       "미수집 (작업자 기억·경험)",     "없음",               "데이터 자체가 없음"],
            ["품질 검사 데이터",  "수기 검사 성적서",              "종이 문서",          "LOT 연계 불가, 분실 위험"],
            ["출하·물류 데이터",  "Excel 출하대장",                "사무실 PC",          "LOT 추적 불가"],
            ["CAD 도면",          "로컬 폴더 저장",                "설계 담당자 PC",     "버전 관리 없음, 공유 불편"],
        ],
        col_widths=[4.0, 4.5, 3.5, 4.0]
    )

    # ══════════════════════════════════════════
    # 섹션 5. 문제점 및 개선 방향
    # ══════════════════════════════════════════
    add_heading(doc, "5. 문제점 및 개선 요구사항 도출", 1)

    add_heading(doc, "5.1 공정별 핵심 문제 요약", 2)
    styled_table(doc,
        ["영역", "핵심 문제", "심각도", "우선순위"],
        [
            ["견적",      "수작업 기반, 리드타임 1일+ 및 담당자별 편차 ±10%",       "상(High)", "1순위"],
            ["공정관리",  "경험 의존 운영, 공정 데이터 미수집으로 개선 근거 없음",  "상(High)", "2순위"],
            ["데이터통합", "ERP-현장 데이터 실시간 미연계, 가시성 부족",            "상(High)", "2순위"],
            ["이력관리",  "LOT 기반 Traceability 체계 미흡, 클레임 대응 취약",     "중(Mid)",  "3순위"],
            ["AI 확장성", "데이터 축적 체계 부재로 제조AI 적용 기반 없음",          "중(Mid)",  "4순위"],
        ],
        col_widths=[3.0, 8.5, 2.5, 2.5]
    )

    add_heading(doc, "5.2 데이터 구조 문제", 2)
    add_body(doc, "현재 데이터 관리 구조의 핵심 문제는 아래와 같다.")
    for item in [
        "생산·품질·설비 데이터가 공정 간 연결 없이 분산 관리됨",
        "CAD 도면 ↔ BOM ↔ 공정 ↔ 원가 ↔ 출하 데이터 연계 부재",
        "LOT 기반 입고-생산-출하 Traceability 체계 미흡",
        "IoT 데이터 미수집으로 AI 학습 데이터 축적 불가",
        "Excel/수기 데이터의 정합성 검증 불가 및 분실 위험",
    ]:
        add_body(doc, item, bullet=True)

    add_heading(doc, "5.3 개선 방향", 2)
    styled_table(doc,
        ["문제 영역", "개선 방향", "TO-BE 목표"],
        [
            ["견적 비효율",    "CAD AI 파이프라인 구축 (YOLOv8+GNN+XGBoost)",       "견적 리드타임 수분, 정확도 ±5%"],
            ["공정 데이터",    "PLC·IoT 기반 공정 데이터 자동 수집 체계 구축",       "실시간 공정 모니터링 가능"],
            ["데이터 통합",    "MES+ERP 통합 Digital Thread 구현",                    "수주~출하 전 공정 실시간 가시성"],
            ["LOT 추적",       "LOT 기반 Traceability DB 구축 + AI Agent 조회",      "클레임 원인 10분 내 추적"],
            ["AI 기반 확장",   "벡터 DB + RAG Agent로 지식 기반 의사결정 지원",      "AI 질의응답 기반 운영 전환"],
        ],
        col_widths=[3.5, 6.5, 6.0]
    )

    # ── 별첨
    doc.add_page_break()
    add_heading(doc, "[별첨] 인터뷰 결과 요약", 1)
    add_body(doc, "아래는 현장 인터뷰 시 수집된 주요 의견을 공정별로 정리한 것이다.")

    styled_table(doc,
        ["인터뷰 대상", "공정", "주요 의견", "개선 희망사항"],
        [
            ["영업 담당자",  "수주·견적", '"도면 보고 견적 내는 데 하루가 걸린다. 비슷한 제품인데도 매번 처음부터 해야 한다."',
             "과거 유사 견적 자동 참조, 빠른 견적 산출"],
            ["자재 담당자",  "입고·재고", '"자재가 어디 있는지 몰라서 현장 뒤지는 경우가 자주 있다."',
             "실시간 재고 위치 확인, LOT 바코드 스캔"],
            ["생산 담당자",  "포밍·용접", '"불량이 나면 왜 났는지 알 수가 없다. 그냥 다시 만든다."',
             "공정 데이터 자동 기록, 불량 원인 추적"],
            ["물류 담당자",  "출하",      '"납기 임박해서야 문제를 알게 된다. 미리 알 수 있으면 좋겠다."',
             "납기 리스크 사전 알림, LOT 추적 조회"],
        ],
        col_widths=[3.0, 2.5, 7.0, 3.5]
    )

    out_path = os.path.join(OUTPUT_DIR, "SF-AD1_현행업무분석서.docx")
    doc.save(out_path)
    print(f"[완료] {out_path}")
    return out_path


# ─────────────────────────────────────────────
# SF-AD2  요구사항정의서
# ─────────────────────────────────────────────

def build_sf_ad2():
    doc = Document()

    for section in doc.sections:
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin   = Cm(3.0)
        section.right_margin  = Cm(2.5)

    add_cover(doc,
              "SF-AD2-001",
              "요구사항정의서",
              "기능·비기능·AI 요구사항 정의 및 우선순위")

    toc = [
        ("1.",    "문서 개요",                           "3"),
        ("1.1",   "목적 및 범위",                        "3"),
        ("1.2",   "요구사항 분류 체계",                  "3"),
        ("1.3",   "요구사항 식별 원칙",                  "4"),
        ("2.",    "이해관계자 분석",                     "4"),
        ("2.1",   "이해관계자 목록",                     "4"),
        ("2.2",   "이해관계자별 주요 요구사항",          "5"),
        ("3.",    "기능 요구사항",                       "5"),
        ("3.1",   "수주·견적 AI 자동화",                 "5"),
        ("3.2",   "입고·재고 관리",                      "7"),
        ("3.3",   "생산·공정 관리",                      "8"),
        ("3.4",   "출하·물류 관리",                      "9"),
        ("3.5",   "AI Agent 통합 관리",                  "10"),
        ("4.",    "비기능 요구사항",                     "11"),
        ("4.1",   "성능 요구사항",                       "11"),
        ("4.2",   "가용성·신뢰성 요구사항",              "12"),
        ("4.3",   "보안 요구사항",                       "12"),
        ("4.4",   "유지보수성 요구사항",                 "13"),
        ("5.",    "AI 성능 요구사항",                    "13"),
        ("5.1",   "CAD 견적 AI 성능 목표",               "13"),
        ("5.2",   "RAG AI Agent 성능 목표",              "14"),
        ("5.3",   "AI 모델 운영 요구사항",               "14"),
        ("[별첨]", "요구사항 목록표 (전체)",              "15"),
    ]
    add_toc_page(doc, toc)

    # ══════════════════════════════════════════
    # 섹션 1. 문서 개요
    # ══════════════════════════════════════════
    add_heading(doc, "1. 문서 개요", 1)

    add_heading(doc, "1.1 목적 및 범위", 2)
    add_body(doc, "본 문서는 부영기업 제조AI 스마트공장 시스템의 이해관계자 요구를 체계적으로 수집·분석하고 "
                  "명확한 요구사항으로 정의하여 설계 및 개발의 기준 문서로 활용함을 목적으로 한다.")

    styled_table(doc,
        ["요구사항 유형", "범위", "요구사항 수"],
        [
            ["기능 요구사항 (FR)",    "5개 도메인 주요 기능",           "52건"],
            ["비기능 요구사항 (NFR)", "성능, 가용성, 보안, 유지보수",   "18건"],
            ["AI 성능 요구사항 (AR)", "CAD AI, RAG Agent 성능 목표",    "12건"],
            ["인터페이스 요구사항",   "ERP 연계, IoT, 외부 시스템",     "8건"],
            ["합계",                  "",                                "90건"],
        ],
        col_widths=[5.0, 7.0, 4.0]
    )

    add_heading(doc, "1.2 요구사항 분류 체계", 2)
    styled_table(doc,
        ["코드 체계", "예시", "설명"],
        [
            ["FR-[도메인]-[번호]", "FR-QT-001", "기능 요구사항 (Functional Requirement)"],
            ["NFR-[유형]-[번호]",  "NFR-PF-001", "비기능 요구사항 (Non-Functional Requirement)"],
            ["AR-[AI유형]-[번호]", "AR-CAD-001", "AI 성능 요구사항 (AI Requirement)"],
            ["IR-[유형]-[번호]",   "IR-ERP-001", "인터페이스 요구사항 (Interface Requirement)"],
        ],
        col_widths=[4.0, 3.5, 8.5]
    )

    add_heading(doc, "1.3 요구사항 식별 원칙", 2)
    for item in [
        "SMART 원칙 적용: Specific, Measurable, Achievable, Relevant, Time-bound",
        "우선순위 분류: Must Have (필수) / Should Have (권장) / Nice to Have (선택)",
        "현행 문제점과 직접 연결: SF-AD1 현행업무분석서의 문제점을 요구사항으로 전환",
        "스마트공장 수준 목표 반영: 기초 → 중간1 수준 달성 기준 적용",
    ]:
        add_body(doc, item, bullet=True)

    # ══════════════════════════════════════════
    # 섹션 2. 이해관계자 분석
    # ══════════════════════════════════════════
    add_heading(doc, "2. 이해관계자 분석", 1)

    add_heading(doc, "2.1 이해관계자 목록", 2)
    styled_table(doc,
        ["이해관계자", "역할", "관심사", "영향력"],
        [
            ["부영기업 대표",   "최종 의사결정권자",      "사업비 ROI, 납기 단축, 품질 향상",   "High"],
            ["생산 관리자",     "생산계획 및 실행 총괄",   "공정 가시성, 실적 집계 자동화",      "High"],
            ["견적 담당자",     "수주·견적 처리",          "견적 자동화, 리드타임 단축",          "High"],
            ["현장 작업자",     "POP 단말 사용자",         "사용 편의성, 입력 최소화",            "Mid"],
            ["품질 담당자",     "품질 검사 및 클레임 대응", "LOT 추적, 불량 원인 분석",           "High"],
            ["물류 담당자",     "출하 관리",               "출하 현황 가시성, 납기 관리",         "Mid"],
            ["IT 관리자",       "시스템 운영·유지보수",    "시스템 안정성, 관리 편의성",          "Mid"],
            ["㈜아이시프트 PM", "시스템 공급 총괄",        "요구사항 충족, 일정 준수",            "High"],
        ],
        col_widths=[3.5, 4.0, 6.5, 2.0]
    )

    add_heading(doc, "2.2 이해관계자별 주요 요구사항", 2)
    styled_table(doc,
        ["이해관계자", "핵심 요구사항"],
        [
            ["부영기업 대표",   "KPI 대시보드, 생산성·품질 지표 실시간 확인, 사업 성과 가시화"],
            ["견적 담당자",     "CAD 도면 업로드만으로 견적 자동 산출, 과거 유사 견적 참조 기능"],
            ["생산 관리자",     "작업지시 자동 생성, 공정 진행 현황 실시간 조회, IoT 모니터링"],
            ["현장 작업자",     "터치 POP 화면 직관성, 최소 입력 단계, 한국어 UI"],
            ["품질 담당자",     "LOT별 생산·검사 이력 원클릭 조회, AI Agent 클레임 원인 분석"],
            ["물류 담당자",     "출하 현황 실시간 조회, 납기 리스크 사전 알림, AI Agent 납기 분석"],
        ],
        col_widths=[3.5, 12.5]
    )

    # ══════════════════════════════════════════
    # 섹션 3. 기능 요구사항
    # ══════════════════════════════════════════
    add_heading(doc, "3. 기능 요구사항", 1)

    add_heading(doc, "3.1 수주·견적 AI 자동화 (도메인: QT)", 2)
    styled_table(doc,
        ["요구사항 ID", "요구사항명", "상세 내용", "우선순위"],
        [
            ["FR-QT-001", "CAD 도면 업로드",         "DWG, PDF 형식 CAD 파일 업로드 및 버전 관리 기능",             "Must"],
            ["FR-QT-002", "CAD 객체 자동 파싱",      "Autodesk API + YOLOv8 병렬 파싱, 홀·슬롯·치수·재질 추출",    "Must"],
            ["FR-QT-003", "객체 인식 결과 검토",     "파싱 결과 시각화, 담당자 수정·확인 기능 (Human-in-the-loop)", "Must"],
            ["FR-QT-004", "BOM 자동 생성",            "GNN 기반 자재 관계 추론으로 BOM 자동 구성, 수동 수정 가능",   "Must"],
            ["FR-QT-005", "견적 자동 산출",           "XGBoost 모델로 공정별 원가·최종 견적 자동 계산",             "Must"],
            ["FR-QT-006", "SHAP 설명 제공",           "원가 영향 변수 Top-5 SHAP 값 시각화 및 설명 텍스트 제공",    "Must"],
            ["FR-QT-007", "유사 견적 검색",           "과거 견적 중 유사 도면·조건 Top-3 자동 검색·비교 표시",      "Should"],
            ["FR-QT-008", "견적서 출력",              "PDF 견적서 자동 생성 및 이메일 발송 기능",                    "Should"],
            ["FR-QT-009", "견적 승인 워크플로우",     "작성→검토→승인 단계별 상태 관리, 알림 발송",                 "Should"],
            ["FR-QT-010", "수주 확정 연계",           "견적 승인 시 ERP 수주 데이터 자동 생성 연계",                "Must"],
        ],
        col_widths=[2.8, 4.2, 7.5, 1.5]
    )

    add_heading(doc, "3.2 입고·재고 관리 (도메인: INV)", 2)
    styled_table(doc,
        ["요구사항 ID", "요구사항명", "상세 내용", "우선순위"],
        [
            ["FR-INV-001", "입고 등록",         "스마트패드 바코드 스캔으로 입고 데이터 등록, LOT 번호 자동 부여", "Must"],
            ["FR-INV-002", "입고 검사 등록",    "검사 항목별 합/부 결과 입력, 불합격 시 반송 처리 워크플로우",    "Must"],
            ["FR-INV-003", "LOT 이력 관리",     "LOT별 입고→보관→생산→출하 전 이력 DB 기록 및 조회",             "Must"],
            ["FR-INV-004", "재고 현황 조회",    "품목별·위치별 실시간 재고 수량 조회 화면",                        "Must"],
            ["FR-INV-005", "재고 위치 관리",    "창고 구역·랙 위치 코드 기반 자재 위치 등록 및 변경",             "Should"],
            ["FR-INV-006", "입고 AI Agent",     "자재 이력·품질 패턴 질의, 이상 입고 원인 분석 자연어 응답",      "Must"],
            ["FR-INV-007", "재고 부족 알림",    "기준 재고량 이하 시 자동 알림 및 발주 권고",                     "Should"],
            ["FR-INV-008", "공급처 품질 분석",  "공급처별 불량률·납기 준수율 분석 리포트",                        "Nice"],
        ],
        col_widths=[2.8, 4.2, 7.5, 1.5]
    )

    add_heading(doc, "3.3 생산·공정 관리 (도메인: PRD)", 2)
    styled_table(doc,
        ["요구사항 ID", "요구사항명", "상세 내용", "우선순위"],
        [
            ["FR-PRD-001", "작업지시 생성",       "수주 확정 시 공정 라우팅 기반 자동 작업지시 생성",               "Must"],
            ["FR-PRD-002", "POP 작업 실적 입력",  "터치 POP에서 작업 시작/종료/수량 입력, 바코드 스캔 지원",        "Must"],
            ["FR-PRD-003", "IoT 공정 데이터 수집", "PLC→Edge→MES 자동 수집 (압력·속도·전류·온도), 1초 주기",       "Must"],
            ["FR-PRD-004", "공정 모니터링 대시보드", "실시간 설비 상태, 공정 진행률, 불량 현황 시각화",             "Must"],
            ["FR-PRD-005", "불량 등록·분류",       "불량 유형·위치·수량 입력, 불량 코드 체계화",                    "Must"],
            ["FR-PRD-006", "공정 데이터 이력 조회", "LOT별 공정 조건 데이터 조회 및 CSV 다운로드",                  "Should"],
            ["FR-PRD-007", "설비 이상 알림",       "설비 센서 임계값 초과 시 현황판·모바일 알림 자동 발송",          "Should"],
            ["FR-PRD-008", "생산 실적 집계",       "일·주·월별 생산량, 가동률, 불량률 자동 집계 리포트",            "Must"],
            ["FR-PRD-009", "작업 표준서 연동",     "작업지시 화면에서 해당 제품 작업표준서(SOP) PDF 바로 보기",     "Should"],
            ["FR-PRD-010", "납기 예측",            "현재 공정 진행 속도 기반 납기 충족 가능성 자동 계산·표시",      "Should"],
        ],
        col_widths=[2.8, 4.2, 7.5, 1.5]
    )

    add_heading(doc, "3.4 출하·물류 관리 (도메인: SHP)", 2)
    styled_table(doc,
        ["요구사항 ID", "요구사항명", "상세 내용", "우선순위"],
        [
            ["FR-SHP-001", "출하 지시 생성",      "수주 납기 기준 자동 출하 지시 생성, 담당자 확인 후 확정",         "Must"],
            ["FR-SHP-002", "출하 검사 등록",       "출하 전 샘플/전수 검사 결과 등록, LOT 연계",                     "Must"],
            ["FR-SHP-003", "LOT 추적 조회",        "LOT 번호로 입고→생산→검사→출하 전 이력 원클릭 조회",             "Must"],
            ["FR-SHP-004", "납기 리스크 분석",     "출하 AI Agent를 통한 납기 지연 위험 LOT 자동 감지·알림",         "Must"],
            ["FR-SHP-005", "출하 현황 대시보드",   "금일/금주 출하 예정, 출하 완료, 미출하 현황 시각화",             "Should"],
            ["FR-SHP-006", "클레임 관리",           "클레임 접수, LOT 연계 원인 분석, 처리 이력 관리",               "Should"],
            ["FR-SHP-007", "출하 AI Agent",         "자연어로 LOT 조회·클레임 원인 분석·납기 리스크 질의 응답",      "Must"],
            ["FR-SHP-008", "거래명세서 자동 생성", "출하 확정 시 거래명세서 자동 생성 및 이메일 발송",               "Should"],
        ],
        col_widths=[2.8, 4.2, 7.5, 1.5]
    )

    add_heading(doc, "3.5 AI Agent 통합 관리 (도메인: AI)", 2)
    styled_table(doc,
        ["요구사항 ID", "요구사항명", "상세 내용", "우선순위"],
        [
            ["FR-AI-001", "통합 AI 질의 인터페이스", "하나의 채팅 UI에서 전 공정 AI 질의 가능",                        "Must"],
            ["FR-AI-002", "RAG 지식베이스 관리",      "SOP·품질기준서·클레임 데이터 임베딩 업로드 및 버전 관리",       "Must"],
            ["FR-AI-003", "질문 이력 관리",            "사용자별 AI 질의 이력 저장, 재조회 및 공유 기능",               "Should"],
            ["FR-AI-004", "AI 답변 품질 평가",         "사용자 답변 평가(좋음/나쁨) 수집, 모델 개선 데이터 활용",      "Should"],
            ["FR-AI-005", "맥락 기반 연속 질의",       "이전 질의 맥락을 유지하며 연속 대화 가능 (멀티턴)",            "Must"],
            ["FR-AI-006", "AI 분석 리포트 생성",       "생산·품질 데이터 기반 주간·월간 AI 자동 분석 리포트",          "Nice"],
        ],
        col_widths=[2.8, 4.2, 7.5, 1.5]
    )

    # ══════════════════════════════════════════
    # 섹션 4. 비기능 요구사항
    # ══════════════════════════════════════════
    add_heading(doc, "4. 비기능 요구사항", 1)

    add_heading(doc, "4.1 성능 요구사항", 2)
    styled_table(doc,
        ["요구사항 ID", "항목", "기준값", "측정 방법"],
        [
            ["NFR-PF-001", "웹 화면 응답시간",      "일반 조회: 3초 이내 / 대용량 리포트: 10초 이내", "Lighthouse 측정"],
            ["NFR-PF-002", "CAD 파싱 처리시간",     "DWG/PDF 1장 기준 60초 이내",                     "API 응답시간 측정"],
            ["NFR-PF-003", "IoT 데이터 수집 주기",  "PLC 데이터 수집 1초 주기, DB 반영 5초 이내",     "Edge 로그 검증"],
            ["NFR-PF-004", "동시 사용자",            "최소 20명 동시 접속 처리",                       "부하 테스트"],
            ["NFR-PF-005", "AI Agent 응답시간",     "일반 질의 30초 이내, 복합 분석 60초 이내",        "API 응답시간 측정"],
        ],
        col_widths=[2.8, 4.2, 6.0, 3.0]
    )

    add_heading(doc, "4.2 가용성·신뢰성 요구사항", 2)
    styled_table(doc,
        ["요구사항 ID", "항목", "기준값", "비고"],
        [
            ["NFR-AV-001", "시스템 가용성",        "99% 이상 (월간 다운타임 7.2시간 이하)",        "클라우드 SLA 준수"],
            ["NFR-AV-002", "Edge 버퍼링",           "네트워크 장애 시 최대 24시간 로컬 버퍼 저장",  "재전송 보장"],
            ["NFR-AV-003", "데이터 백업",           "일 1회 자동 백업, 30일 보관",                  "AWS S3 저장"],
            ["NFR-AV-004", "장애 복구 목표 시간",   "RTO: 4시간 이내, RPO: 1시간 이내",             "DR 계획 수립"],
        ],
        col_widths=[2.8, 4.2, 6.0, 3.0]
    )

    add_heading(doc, "4.3 보안 요구사항", 2)
    styled_table(doc,
        ["요구사항 ID", "항목", "내용", "우선순위"],
        [
            ["NFR-SC-001", "사용자 인증",       "ID/PW + 역할 기반 접근 제어 (RBAC)",            "Must"],
            ["NFR-SC-002", "데이터 암호화",     "전송 데이터 TLS 1.2+, DB 민감정보 AES-256 암호화", "Must"],
            ["NFR-SC-003", "감사 로그",         "주요 데이터 변경·삭제 이력 6개월 이상 보관",    "Must"],
            ["NFR-SC-004", "API 보안",          "API Key + JWT 인증, Rate Limiting 적용",         "Must"],
        ],
        col_widths=[2.8, 3.5, 7.0, 2.7]
    )

    add_heading(doc, "4.4 유지보수성 요구사항", 2)
    styled_table(doc,
        ["요구사항 ID", "항목", "내용"],
        [
            ["NFR-MT-001", "운영 매뉴얼",         "시스템 관리자·사용자 매뉴얼 제공 (한국어)"],
            ["NFR-MT-002", "AI 모델 재학습",       "누적 데이터 기반 정기 재학습 파이프라인 구축 (분기 1회)"],
            ["NFR-MT-003", "모니터링 대시보드",    "서버 CPU·메모리·디스크 사용량 실시간 모니터링"],
            ["NFR-MT-004", "시스템 교육",          "사용자 그룹별 맞춤 교육 1회 이상 제공"],
        ],
        col_widths=[2.8, 4.2, 9.0]
    )

    # ══════════════════════════════════════════
    # 섹션 5. AI 성능 요구사항
    # ══════════════════════════════════════════
    add_heading(doc, "5. AI 성능 요구사항", 1)

    add_heading(doc, "5.1 CAD 견적 AI 성능 목표", 2)
    styled_table(doc,
        ["요구사항 ID", "AI 항목", "성능 목표", "측정 지표", "검증 방법"],
        [
            ["AR-CAD-001", "CAD 객체 인식 정확도", "80% 이상",    "F1 Score (IoU 0.5 기준)",  "테스트셋 100건 검증"],
            ["AR-CAD-002", "견적 산출 정확도",      "±5% 이내",   "MAPE",                      "실제 원가 비교 50건"],
            ["AR-CAD-003", "BOM 생성 정확도",        "85% 이상",   "Precision/Recall/F1",       "실제 BOM 비교 50건"],
            ["AR-CAD-004", "납기 예측 정확도",       "85% 이상",   "MAPE",                      "실제 납기 비교 30건"],
            ["AR-CAD-005", "SHAP 설명 신뢰도",       "90% 일치율", "전문가 평가 일치율",        "전문가 검토 10건"],
            ["AR-CAD-006", "견적 리드타임",           "5분 이내",   "API 처리시간",              "성능 테스트"],
        ],
        col_widths=[2.8, 3.8, 2.5, 3.0, 4.0]
    )

    add_heading(doc, "5.2 RAG AI Agent 성능 목표", 2)
    styled_table(doc,
        ["요구사항 ID", "AI 항목", "성능 목표", "측정 지표", "검증 방법"],
        [
            ["AR-RAG-001", "질의 응답 정확도",   "85% 이상",  "사용자 평가 정확도",     "사용자 평가 100건"],
            ["AR-RAG-002", "문서 검색 관련도",   "90% 이상",  "Precision@5",            "수동 관련도 평가"],
            ["AR-RAG-003", "응답 시간",           "30초 이내", "API P95 응답시간",       "부하 테스트"],
            ["AR-RAG-004", "환각(Hallucination) 방지", "5% 이하", "오답률 수동 검증",   "전문가 검토 50건"],
            ["AR-RAG-005", "멀티턴 맥락 유지",   "3턴 이상",  "맥락 정확도 평가",       "시나리오 테스트"],
            ["AR-RAG-006", "한국어 응답 품질",   "자연스러운 한국어", "전문가 언어 평가", "평가단 검토"],
        ],
        col_widths=[2.8, 3.8, 2.5, 3.0, 4.0]
    )

    add_heading(doc, "5.3 AI 모델 운영 요구사항", 2)
    styled_table(doc,
        ["요구사항 ID", "항목", "내용"],
        [
            ["AR-OPS-001", "Human-in-the-loop",  "AI 추천값 관리자 검토·수정·승인 후 운영 반영 필수"],
            ["AR-OPS-002", "모델 버전 관리",      "AI 모델 버전별 성능 지표 기록, 롤백 기능"],
            ["AR-OPS-003", "데이터 드리프트 감지", "입력 데이터 분포 변화 감지 시 알림 및 재학습 권고"],
            ["AR-OPS-004", "AI 결과 설명",        "모든 AI 추천에 근거 설명 제공 (Explainable AI)"],
            ["AR-OPS-005", "재학습 데이터 관리",  "운영 중 수집 데이터 학습용 레이블링 및 품질 관리"],
        ],
        col_widths=[2.8, 4.0, 9.2]
    )

    # ── 별첨: 요구사항 전체 목록표
    doc.add_page_break()
    add_heading(doc, "[별첨] 요구사항 목록표 (전체)", 1)
    add_body(doc, "아래는 본 프로젝트의 전체 요구사항 목록이다. 각 요구사항의 이행 현황은 설계·개발 단계에서 추적 관리한다.")

    all_reqs = [
        # ID, 유형, 도메인, 요구사항명, 우선순위, 관련 기능
        ["FR-QT-001", "기능", "수주·견적", "CAD 도면 업로드",          "Must",   "파일 관리"],
        ["FR-QT-002", "기능", "수주·견적", "CAD 객체 자동 파싱",       "Must",   "AI 파이프라인"],
        ["FR-QT-003", "기능", "수주·견적", "객체 인식 결과 검토",      "Must",   "Human-in-loop"],
        ["FR-QT-004", "기능", "수주·견적", "BOM 자동 생성",            "Must",   "GNN 모델"],
        ["FR-QT-005", "기능", "수주·견적", "견적 자동 산출",           "Must",   "XGBoost 모델"],
        ["FR-QT-006", "기능", "수주·견적", "SHAP 설명 제공",           "Must",   "Explainable AI"],
        ["FR-QT-007", "기능", "수주·견적", "유사 견적 검색",           "Should", "Vector 검색"],
        ["FR-QT-008", "기능", "수주·견적", "견적서 출력",              "Should", "문서 생성"],
        ["FR-QT-009", "기능", "수주·견적", "견적 승인 워크플로우",     "Should", "프로세스"],
        ["FR-QT-010", "기능", "수주·견적", "수주 확정 연계",           "Must",   "ERP 연계"],
        ["FR-INV-001", "기능", "입고·재고", "입고 등록",               "Must",   "바코드 스캔"],
        ["FR-INV-002", "기능", "입고·재고", "입고 검사 등록",          "Must",   "품질 관리"],
        ["FR-INV-003", "기능", "입고·재고", "LOT 이력 관리",           "Must",   "Traceability"],
        ["FR-INV-004", "기능", "입고·재고", "재고 현황 조회",          "Must",   "재고 관리"],
        ["FR-INV-005", "기능", "입고·재고", "재고 위치 관리",          "Should", "창고 관리"],
        ["FR-INV-006", "기능", "입고·재고", "입고 AI Agent",           "Must",   "RAG Agent"],
        ["FR-INV-007", "기능", "입고·재고", "재고 부족 알림",          "Should", "알림"],
        ["FR-INV-008", "기능", "입고·재고", "공급처 품질 분석",        "Nice",   "분석 리포트"],
        ["FR-PRD-001", "기능", "생산·공정", "작업지시 생성",           "Must",   "생산 계획"],
        ["FR-PRD-002", "기능", "생산·공정", "POP 작업 실적 입력",      "Must",   "현장 입력"],
        ["FR-PRD-003", "기능", "생산·공정", "IoT 공정 데이터 수집",    "Must",   "PLC 연계"],
        ["FR-PRD-004", "기능", "생산·공정", "공정 모니터링 대시보드",  "Must",   "시각화"],
        ["FR-PRD-005", "기능", "생산·공정", "불량 등록·분류",          "Must",   "품질 관리"],
        ["FR-PRD-008", "기능", "생산·공정", "생산 실적 집계",          "Must",   "리포트"],
        ["FR-SHP-001", "기능", "출하·물류", "출하 지시 생성",          "Must",   "출하 관리"],
        ["FR-SHP-003", "기능", "출하·물류", "LOT 추적 조회",           "Must",   "Traceability"],
        ["FR-SHP-004", "기능", "출하·물류", "납기 리스크 분석",        "Must",   "AI Agent"],
        ["FR-SHP-007", "기능", "출하·물류", "출하 AI Agent",           "Must",   "RAG Agent"],
        ["FR-AI-001",  "기능", "AI 통합",  "통합 AI 질의 인터페이스",  "Must",   "채팅 UI"],
        ["FR-AI-002",  "기능", "AI 통합",  "RAG 지식베이스 관리",      "Must",   "Vector DB"],
        ["NFR-PF-001", "비기능", "성능",  "웹 화면 응답시간 3초 이내", "Must",   "성능"],
        ["NFR-PF-003", "비기능", "성능",  "IoT 수집 1초 주기",         "Must",   "실시간성"],
        ["NFR-AV-001", "비기능", "가용성", "가용성 99% 이상",          "Must",   "SLA"],
        ["NFR-SC-001", "비기능", "보안",  "RBAC 인증·접근제어",        "Must",   "보안"],
        ["AR-CAD-001", "AI성능", "견적AI", "CAD 객체 인식 80% 이상",   "Must",   "AI 검증"],
        ["AR-CAD-002", "AI성능", "견적AI", "견적 정확도 ±5% 이내",     "Must",   "AI 검증"],
        ["AR-RAG-001", "AI성능", "RAG",   "질의 응답 정확도 85% 이상", "Must",   "AI 검증"],
    ]
    styled_table(doc,
        ["요구사항 ID", "유형", "도메인", "요구사항명", "우선순위", "관련 기능"],
        all_reqs,
        col_widths=[2.8, 1.8, 2.5, 5.5, 1.8, 2.6]
    )

    out_path = os.path.join(OUTPUT_DIR, "SF-AD2_요구사항정의서.docx")
    doc.save(out_path)
    print(f"[완료] {out_path}")
    return out_path


# ─────────────────────────────────────────────
# SF-AD3  기능대비표
# ─────────────────────────────────────────────

def build_sf_ad3():
    doc = Document()

    for section in doc.sections:
        section.top_margin    = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.0)

    add_cover(doc,
              "SF-AD3-001",
              "기능대비표",
              "현행 기능 vs TO-BE 개발 기능 비교 분석")

    toc = [
        ("1.",    "문서 개요",                              "3"),
        ("1.1",   "목적 및 작성 기준",                      "3"),
        ("1.2",   "기능 분류 체계",                         "3"),
        ("2.",    "기능 현황 분석 요약",                    "4"),
        ("2.1",   "현행 기능 보유 현황",                   "4"),
        ("2.2",   "TO-BE 기능 구현 범위",                  "4"),
        ("3.",    "도메인별 기능 대비표",                   "5"),
        ("3.1",   "수주·견적 AI 도메인",                   "5"),
        ("3.2",   "입고·재고 관리 도메인",                 "6"),
        ("3.3",   "생산·공정 관리 도메인",                 "7"),
        ("3.4",   "출하·물류 관리 도메인",                 "8"),
        ("4.",    "AI 기능 신규 개발 목록",                 "9"),
        ("[별첨]", "전체 기능 대비표",                      "10"),
    ]
    add_toc_page(doc, toc)

    # ══════════════════════════════════════════
    # 섹션 1. 문서 개요
    # ══════════════════════════════════════════
    add_heading(doc, "1. 문서 개요", 1)

    add_heading(doc, "1.1 목적 및 작성 기준", 2)
    add_body(doc, "본 문서는 부영기업의 현행(AS-IS) 기능과 구축 예정(TO-BE) 기능을 항목별로 대비하여 "
                  "신규 개발 범위, 개선 범위, 폐기 범위를 명확히 정의하고 개발 우선순위 결정의 기초 자료로 활용한다.")

    styled_table(doc,
        ["구분", "설명", "표기"],
        [
            ["신규 개발 (New)",    "현행에 없는 기능으로 새로 개발",               "N"],
            ["기능 개선 (Improve)", "현행 기능이 있으나 수준 향상·자동화 적용",   "I"],
            ["유지 (Keep)",        "현행 기능을 그대로 유지 (이관 또는 연계)",    "K"],
            ["폐기 (Drop)",        "TO-BE에서 사용하지 않을 현행 방식",           "D"],
        ],
        col_widths=[4.0, 9.0, 3.0]
    )

    add_heading(doc, "1.2 기능 분류 체계", 2)
    styled_table(doc,
        ["대분류", "중분류", "코드 체계"],
        [
            ["수주·견적",  "CAD AI 파이프라인, BOM 관리, 견적 산출, 수주 처리",      "QT"],
            ["입고·재고",  "입고 검사, LOT 관리, 재고 관리, AI Agent",               "INV"],
            ["생산·공정",  "작업지시, POP 실적, IoT 수집, 모니터링, 불량 관리",      "PRD"],
            ["출하·물류",  "출하 지시, LOT 추적, 품질 검증, AI Agent, 클레임",       "SHP"],
            ["AI 통합",    "CAD AI, RAG Agent, 지식베이스, 통합 채팅",               "AI"],
            ["공통 기반",  "대시보드, KPI, 사용자 관리, 알림, 시스템 설정",          "SYS"],
        ],
        col_widths=[3.0, 9.0, 4.0]
    )

    # ══════════════════════════════════════════
    # 섹션 2. 기능 현황 분석 요약
    # ══════════════════════════════════════════
    add_heading(doc, "2. 기능 현황 분석 요약", 1)

    add_heading(doc, "2.1 현행 기능 보유 현황", 2)
    styled_table(doc,
        ["도메인", "현행 지원 기능", "현행 방식", "자동화 수준"],
        [
            ["수주·견적",  "견적 산출, 수주 입력",    "수작업 (Excel, 이메일)",     "수동 (0%)"],
            ["입고·재고",  "입고 기록, 재고 파악",    "수기 기록, Excel",           "수동 (0%)"],
            ["생산·공정",  "작업지시 (일부), 실적 기록", "ERP 일부 + 수기",         "부분 (~10%)"],
            ["출하·물류",  "출하 기록, 납기 확인",    "Excel + 수기",               "수동 (0%)"],
            ["AI 기능",    "없음",                    "—",                          "없음"],
            ["대시보드",   "없음",                    "—",                          "없음"],
        ],
        col_widths=[3.0, 5.0, 5.0, 3.0]
    )

    add_heading(doc, "2.2 TO-BE 기능 구현 범위 요약", 2)
    styled_table(doc,
        ["도메인", "신규 (N)", "개선 (I)", "유지 (K)", "합계"],
        [
            ["수주·견적 AI",  "8건", "2건", "1건", "11건"],
            ["입고·재고",     "5건", "3건", "0건",  "8건"],
            ["생산·공정",     "6건", "4건", "1건", "11건"],
            ["출하·물류",     "5건", "3건", "0건",  "8건"],
            ["AI 통합",       "6건", "0건", "0건",  "6건"],
            ["공통 기반",     "4건", "1건", "1건",  "6건"],
            ["합계",         "34건", "13건", "3건", "50건"],
        ],
        col_widths=[3.5, 2.5, 2.5, 2.5, 5.0]
    )

    # ══════════════════════════════════════════
    # 섹션 3. 도메인별 기능 대비표
    # ══════════════════════════════════════════
    add_heading(doc, "3. 도메인별 기능 대비표", 1)

    add_heading(doc, "3.1 수주·견적 AI 도메인 (QT)", 2)
    styled_table(doc,
        ["기능 ID", "기능명", "AS-IS 현행 기능", "TO-BE 개발 기능", "구분", "비고"],
        [
            ["QT-001", "CAD 도면 관리",     "로컬 PC 폴더 저장, 이메일 수신",       "DWG/PDF 업로드, 버전 관리, 중앙 저장소",     "I", "클라우드 S3"],
            ["QT-002", "도면 자동 파싱",    "없음 (수작업 해석)",                    "Autodesk API + YOLOv8 자동 파싱",           "N", "AI 핵심"],
            ["QT-003", "객체 인식·검토",    "없음",                                  "파싱 결과 시각화, 수정 UI, 신뢰도 표시",    "N", "Human-in-loop"],
            ["QT-004", "BOM 생성",          "수작업 자재 목록 작성 (Excel)",         "GNN 기반 BOM 자동 생성, 수동 수정",         "N", "GNN 모델"],
            ["QT-005", "견적 산출",         "경험 기반 수동 계산 (1일+)",            "XGBoost 견적 자동 산출 (5분 이내)",         "N", "AI 모델"],
            ["QT-006", "원가 설명",         "없음",                                  "SHAP 기반 원가 영향 변수 시각화",           "N", "XAI"],
            ["QT-007", "유사 견적 참조",    "없음 (기억에 의존)",                    "Vector 검색 기반 유사 견적 Top-3 조회",     "N", "RAG"],
            ["QT-008", "견적서 출력",       "Excel 수기 작성 후 PDF 변환",           "자동 PDF 견적서 생성, 이메일 발송",         "I", "자동화"],
            ["QT-009", "수주 확정",         "이메일/구두 확정, 수동 ERP 입력",       "견적 승인 시 ERP 자동 수주 생성",          "I", "ERP 연계"],
            ["QT-010", "납기 예측",         "없음 (경험 기반 답변)",                 "ML 기반 공정 소요시간 예측 및 납기 산출",  "N", "예측 모델"],
            ["QT-011", "수주 이력 조회",    "ERP 기본 조회",                         "ERP 연계 확장 조회, CAD 연계 조회",        "K", "ERP 유지"],
        ],
        col_widths=[1.8, 3.2, 4.5, 4.8, 1.2, 2.0]
    )

    add_heading(doc, "3.2 입고·재고 관리 도메인 (INV)", 2)
    styled_table(doc,
        ["기능 ID", "기능명", "AS-IS 현행 기능", "TO-BE 개발 기능", "구분", "비고"],
        [
            ["INV-001", "입고 등록",       "수기 입고대장, Excel 입력",             "스마트패드 바코드 스캔, LOT 자동 부여",    "I", "디지털화"],
            ["INV-002", "입고 검사",       "육안 검사, 수기 기록",                  "검사 항목 전산 입력, 불합격 워크플로우",  "I", "체계화"],
            ["INV-003", "LOT 추적",        "없음 (LOT 수기 메모)",                  "입고~출하 전 이력 DB 관리, 원클릭 조회", "N", "핵심"],
            ["INV-004", "재고 현황",       "Excel 일 1회 수동 갱신",               "실시간 재고 수량·위치 조회 화면",         "I", "실시간화"],
            ["INV-005", "재고 위치",       "경험 기반 위치 배정",                   "창고 구역/랙 코드 기반 위치 관리",       "N", ""],
            ["INV-006", "입고 AI Agent",   "없음",                                  "자재 이력·품질 패턴 자연어 질의응답",    "N", "RAG"],
            ["INV-007", "재고 알림",       "없음",                                  "기준 재고 이하 시 자동 알림·발주 권고",   "N", ""],
            ["INV-008", "공급처 분석",     "없음",                                  "공급처별 불량률·납기 준수율 리포트",      "N", ""],
        ],
        col_widths=[1.8, 3.2, 4.5, 4.8, 1.2, 2.0]
    )

    add_heading(doc, "3.3 생산·공정 관리 도메인 (PRD)", 2)
    styled_table(doc,
        ["기능 ID", "기능명", "AS-IS 현행 기능", "TO-BE 개발 기능", "구분", "비고"],
        [
            ["PRD-001", "작업지시",          "ERP 일부 입력, 수기",                 "수주 연계 자동 작업지시 생성",            "I", "자동화"],
            ["PRD-002", "POP 실적 입력",     "없음 (구두·수기 보고)",               "터치 POP 실적 입력, 바코드 스캔",        "N", "핵심"],
            ["PRD-003", "IoT 데이터 수집",   "없음 (데이터 미수집)",                "PLC→Edge→MES 자동 수집, 1초 주기",      "N", "핵심 인프라"],
            ["PRD-004", "공정 모니터링",     "없음 (현장 직접 확인)",               "실시간 설비 상태, 진행률 대시보드",      "N", ""],
            ["PRD-005", "불량 관리",         "수기 불량 기록 (간헐적)",             "불량 유형·LOT 연계 등록, 통계 분석",     "I", ""],
            ["PRD-006", "공정 이력 조회",    "없음",                                "LOT별 공정 조건 데이터 조회·다운로드",   "N", ""],
            ["PRD-007", "설비 알림",         "없음",                                "임계값 초과 시 현황판·모바일 자동 알림", "N", ""],
            ["PRD-008", "생산 실적 집계",    "수기 집계, Excel 정리",              "일·주·월 자동 집계 리포트",               "I", "자동화"],
            ["PRD-009", "SOP 연동",          "종이 작업표준서",                     "POP에서 디지털 SOP 바로 보기",           "I", ""],
            ["PRD-010", "납기 예측 연동",    "없음",                                "공정 진행 속도 기반 납기 충족률 표시",   "N", ""],
            ["PRD-011", "현황판",            "없음",                                "생산·품질·설비 KPI 실시간 현황판",       "N", "대형 모니터"],
        ],
        col_widths=[1.8, 3.2, 4.5, 4.8, 1.2, 2.0]
    )

    add_heading(doc, "3.4 출하·물류 관리 도메인 (SHP)", 2)
    styled_table(doc,
        ["기능 ID", "기능명", "AS-IS 현행 기능", "TO-BE 개발 기능", "구분", "비고"],
        [
            ["SHP-001", "출하 지시",      "수기/이메일 출하 지시",                  "수주 납기 기준 자동 출하 지시 생성",       "I", ""],
            ["SHP-002", "출하 검사",      "샘플 육안 검사, 수기",                   "전산 검사 결과 등록, LOT 연계",           "I", ""],
            ["SHP-003", "LOT 추적",       "없음 (출하 이력 Excel)",                 "입고~출하 전 이력 원클릭 조회",           "N", "핵심"],
            ["SHP-004", "납기 리스크",    "없음 (임박해서 인지)",                   "AI Agent 기반 납기 지연 위험 사전 감지",  "N", "AI"],
            ["SHP-005", "출하 대시보드",  "없음",                                   "출하 예정·완료·미출하 현황 시각화",       "N", ""],
            ["SHP-006", "클레임 관리",    "수기 기록, 기억 의존",                   "클레임 접수·LOT 연계 원인 분석·이력",    "N", ""],
            ["SHP-007", "출하 AI Agent", "없음",                                    "자연어 LOT 조회·클레임 분석·납기 질의",  "N", "RAG"],
            ["SHP-008", "거래명세서",     "수동 작성",                              "출하 확정 시 자동 생성·이메일 발송",      "I", "자동화"],
        ],
        col_widths=[1.8, 3.2, 4.5, 4.8, 1.2, 2.0]
    )

    # ══════════════════════════════════════════
    # 섹션 4. AI 기능 신규 개발 목록
    # ══════════════════════════════════════════
    add_heading(doc, "4. AI 기능 신규 개발 목록", 1)
    add_body(doc, "본 프로젝트에서 신규로 개발되는 AI 기능은 아래와 같이 2개 핵심 AI 시스템으로 구성된다.")

    styled_table(doc,
        ["AI 시스템", "기능명", "기술 스택", "입력", "출력", "우선순위"],
        [
            ["CAD 견적 AI", "CAD 도면 자동 파싱",    "YOLOv8 + Autodesk API",  "DWG/PDF",         "객체 인식 결과",      "1순위"],
            ["CAD 견적 AI", "BOM 자동 생성",          "GNN (Graph Neural Net)", "CAD 객체 데이터", "BOM 리스트",          "1순위"],
            ["CAD 견적 AI", "견적 자동 산출",          "XGBoost",                "BOM + 원가 데이터","공정별 견적 금액",   "1순위"],
            ["CAD 견적 AI", "원가 설명 (SHAP)",        "SHAP",                   "XGBoost 모델",    "변수 중요도 차트",    "1순위"],
            ["CAD 견적 AI", "납기 예측",               "Prophet / ML",           "공정 데이터",     "납기 예측일",         "2순위"],
            ["CAD 견적 AI", "유사 견적 검색",          "pgvector 유사도 검색",   "현재 도면 특징",  "유사 견적 Top-3",     "2순위"],
            ["RAG AI Agent", "입고 AI Agent",         "LangChain + pgvector",   "자연어 질의",     "자재·품질 답변",      "1순위"],
            ["RAG AI Agent", "출하 AI Agent",         "LangChain + pgvector",   "자연어 질의",     "LOT·납기 답변",       "1순위"],
            ["RAG AI Agent", "통합 AI 채팅",           "LangGraph",              "자연어 질의",     "멀티도메인 답변",     "2순위"],
            ["RAG AI Agent", "지식베이스 관리",        "pgvector + 임베딩",      "SOP·기준서 문서", "Vector 임베딩 DB",    "1순위"],
            ["RAG AI Agent", "AI 분석 리포트",         "LLM + 데이터 파이프라인", "공정·품질 데이터", "자동 분석 리포트", "3순위"],
        ],
        col_widths=[2.5, 3.5, 3.5, 3.0, 3.5, 1.5]
    )

    # ── 별첨: 전체 기능 대비표
    doc.add_page_break()
    add_heading(doc, "[별첨] 전체 기능 대비표 (요약)", 1)
    add_body(doc, "전체 기능을 구분(N/I/K/D)별로 집계한 요약표이다.")

    all_features = [
        # ID, 기능명, AS-IS, TO-BE, 구분
        ["QT-001", "CAD 도면 관리",        "로컬 PC 저장",         "클라우드 중앙 저장소",         "I"],
        ["QT-002", "도면 자동 파싱",       "없음 (수작업)",        "YOLOv8 + Autodesk API",        "N"],
        ["QT-003", "객체 인식 검토",       "없음",                 "파싱 결과 UI, Human-in-loop",  "N"],
        ["QT-004", "BOM 자동 생성",        "수작업 Excel",         "GNN 기반 자동 생성",           "N"],
        ["QT-005", "견적 자동 산출",       "경험 기반 수동",       "XGBoost 모델, 5분 이내",       "N"],
        ["QT-006", "원가 SHAP 설명",       "없음",                 "SHAP 변수 중요도 시각화",      "N"],
        ["QT-007", "유사 견적 검색",       "없음",                 "Vector 유사도 검색",           "N"],
        ["QT-008", "견적서 자동 출력",     "Excel 수기 작성",      "PDF 자동 생성·이메일",         "I"],
        ["QT-009", "수주 ERP 연계",        "수동 ERP 입력",        "견적 승인 시 자동 생성",       "I"],
        ["QT-010", "납기 예측",            "없음",                 "ML 기반 납기 산출",            "N"],
        ["INV-001", "입고 등록",           "수기 기록",            "바코드 스캔 전산 등록",        "I"],
        ["INV-002", "입고 검사",           "육안 수기",            "검사 항목 전산, 워크플로우",   "I"],
        ["INV-003", "LOT 추적",            "없음",                 "전 이력 DB 관리",              "N"],
        ["INV-004", "재고 현황",           "Excel 수동",           "실시간 재고 조회",             "I"],
        ["INV-006", "입고 AI Agent",       "없음",                 "RAG 자연어 질의",              "N"],
        ["PRD-001", "작업지시",            "ERP 일부+수기",        "수주 연계 자동 생성",          "I"],
        ["PRD-002", "POP 실적 입력",       "없음",                 "터치 POP 전산 입력",           "N"],
        ["PRD-003", "IoT 수집",            "없음",                 "PLC→Edge→MES 자동 수집",       "N"],
        ["PRD-004", "공정 모니터링",       "없음",                 "실시간 대시보드",              "N"],
        ["PRD-005", "불량 관리",           "수기 간헐 기록",       "LOT 연계 불량 등록·통계",      "I"],
        ["PRD-008", "생산 실적 집계",      "수기 Excel",           "자동 집계 리포트",             "I"],
        ["PRD-011", "현황판",              "없음",                 "실시간 KPI 현황판",            "N"],
        ["SHP-001", "출하 지시",           "수기/이메일",          "수주 기반 자동 생성",          "I"],
        ["SHP-003", "LOT 추적",            "없음",                 "전 이력 원클릭 조회",          "N"],
        ["SHP-004", "납기 리스크",         "없음",                 "AI Agent 사전 감지",           "N"],
        ["SHP-006", "클레임 관리",         "수기·기억",            "전산 접수·LOT 원인 분석",      "N"],
        ["SHP-007", "출하 AI Agent",       "없음",                 "RAG 자연어 질의",              "N"],
        ["AI-001",  "통합 AI 채팅",        "없음",                 "LangGraph 멀티도메인 채팅",    "N"],
        ["AI-002",  "지식베이스 관리",     "없음",                 "pgvector 임베딩 관리",         "N"],
        ["SYS-001", "KPI 대시보드",        "없음",                 "생산·품질·출하 KPI 시각화",    "N"],
        ["SYS-002", "사용자/권한 관리",    "없음",                 "RBAC 사용자 관리",             "N"],
        ["SYS-003", "알림 시스템",         "없음",                 "모바일·현황판 자동 알림",      "N"],
    ]

    styled_table(doc,
        ["기능 ID", "기능명", "AS-IS 현행", "TO-BE 개발", "구분(N/I/K)"],
        all_features,
        col_widths=[2.0, 3.5, 4.0, 5.5, 2.0]
    )

    out_path = os.path.join(OUTPUT_DIR, "SF-AD3_기능대비표.docx")
    doc.save(out_path)
    print(f"[완료] {out_path}")
    return out_path


# ─────────────────────────────────────────────
# 실행 진입점
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("부영기업 AI MES - 분석단계 문서 생성")
    print("=" * 60)
    p1 = build_sf_ad1()
    p2 = build_sf_ad2()
    p3 = build_sf_ad3()
    print()
    print("생성 완료:")
    print(f"  {p1}")
    print(f"  {p2}")
    print(f"  {p3}")
