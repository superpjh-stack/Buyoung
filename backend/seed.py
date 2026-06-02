"""
초기 seed 데이터 삽입 스크립트 — 각 엔티티 10개
실행: python seed.py
"""
import os, sys, json
os.environ["PGPASSFILE"] = "NUL"
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from sqlalchemy import create_engine, text
from passlib.context import CryptContext

DB_URL = "postgresql+pg8000://buyoung:password@localhost:5432/buyoung_mes"
engine = create_engine(DB_URL, echo=False)
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def run(conn, label, sql, params=None):
    try:
        conn.execute(text(sql), params or {})
        print(f"  [OK] {label}")
    except Exception as e:
        msg = str(e)
        if "already exists" in msg or "duplicate" in msg.lower() or "unique" in msg.lower():
            print(f"  [SKIP] {label} (이미 존재)")
        else:
            print(f"  [ERR] {label}: {msg[:150]}")
        conn.execute(text("ROLLBACK TO sp"))
    conn.execute(text("SAVEPOINT sp"))


with engine.connect() as conn:
    conn.execute(text("BEGIN"))
    conn.execute(text("SAVEPOINT sp"))

    # ── 1. Users (10명) ──────────────────────────────────────────────────────
    print("\n[1] 사용자 10명 생성")
    users = [
        ("00000001-0000-0000-0001-000000000001", "admin",      "ADMIN",    "관리부",  "홍길동"),
        ("00000001-0000-0000-0001-000000000002", "manager",    "MANAGER",  "생산부",  "김생산"),
        ("00000001-0000-0000-0001-000000000003", "operator1",  "OPERATOR", "생산부",  "이성형"),
        ("00000001-0000-0000-0001-000000000004", "operator2",  "OPERATOR", "생산부",  "박용접"),
        ("00000001-0000-0000-0001-000000000005", "inspector",  "INSPECTOR","품질부",  "최검사"),
        ("00000001-0000-0000-0001-000000000006", "operator3",  "OPERATOR", "생산부",  "정절단"),
        ("00000001-0000-0000-0001-000000000007", "operator4",  "OPERATOR", "생산부",  "강포장"),
        ("00000001-0000-0000-0001-000000000008", "inspector2", "INSPECTOR","품질부",  "윤품질"),
        ("00000001-0000-0000-0001-000000000009", "manager2",   "MANAGER",  "영업부",  "임영업"),
        ("00000001-0000-0000-0001-000000000010", "operator5",  "OPERATOR", "입고부",  "한입고"),
    ]
    for uid, username, role, dept, name in users:
        run(conn, f"user:{username}", """
            INSERT INTO users (user_id, username, password_hash, role, department, is_deleted)
            VALUES (:uid, :username, :pw, :role, :dept, false)
            ON CONFLICT (username) DO NOTHING
        """, {"uid": uid, "username": username,
              "pw": pwd.hash("password1234"), "role": role, "dept": dept})

    # ── 2. Supplier (10개) ────────────────────────────────────────────────────
    print("\n[2] 공급처 10개 생성")
    suppliers = [
        ("00000002-0000-0000-0001-000000000001", "SUP-001", "한국철강(주)",       0.92),
        ("00000002-0000-0000-0001-000000000002", "SUP-002", "대한금속소재",       0.85),
        ("00000002-0000-0000-0001-000000000003", "SUP-003", "삼성와이어(주)",     0.95),
        ("00000002-0000-0000-0001-000000000004", "SUP-004", "포스코스틸(주)",     0.97),
        ("00000002-0000-0000-0001-000000000005", "SUP-005", "동국제강",           0.88),
        ("00000002-0000-0000-0001-000000000006", "SUP-006", "현대제철소재",       0.91),
        ("00000002-0000-0000-0001-000000000007", "SUP-007", "KSM 부품",           0.79),
        ("00000002-0000-0000-0001-000000000008", "SUP-008", "세아베스틸",         0.93),
        ("00000002-0000-0000-0001-000000000009", "SUP-009", "풍산금속",           0.86),
        ("00000002-0000-0000-0001-000000000010", "SUP-010", "고려특수강",         0.89),
    ]
    for sid, code, name, score in suppliers:
        run(conn, f"supplier:{code}", """
            INSERT INTO supplier (supplier_id, supplier_code, supplier_name, quality_score, is_deleted)
            VALUES (:sid, :code, :name, :score, false)
            ON CONFLICT (supplier_code) DO NOTHING
        """, {"sid": sid, "code": code, "name": name, "score": score})

    # ── 3. Material (10개) ────────────────────────────────────────────────────
    print("\n[3] 원자재 10개 생성")
    materials = [
        ("00000003-0000-0000-0001-000000000001", "MAT-SS400-2T",  "SS400 코일 2T",      "COIL",  "M",   4800),
        ("00000003-0000-0000-0001-000000000002", "MAT-SS400-3T",  "SS400 코일 3T",      "COIL",  "M",   7200),
        ("00000003-0000-0000-0001-000000000003", "MAT-WIRE-08",   "용접 와이어 0.8mm",  "WIRE",  "KG",  3500),
        ("00000003-0000-0000-0001-000000000004", "MAT-BOLT-M10",  "볼트 M10",           "BOLT",  "EA",    50),
        ("00000003-0000-0000-0001-000000000005", "MAT-PAINT-GY",  "회색 도료",          "PAINT", "L",   8000),
        ("00000003-0000-0000-0001-000000000006", "MAT-SS400-1.5T","SS400 코일 1.5T",    "COIL",  "M",   3600),
        ("00000003-0000-0000-0001-000000000007", "MAT-WIRE-12",   "용접 와이어 1.2mm",  "WIRE",  "KG",  4200),
        ("00000003-0000-0000-0001-000000000008", "MAT-BOLT-M8",   "볼트 M8",            "BOLT",  "EA",    35),
        ("00000003-0000-0000-0001-000000000009", "MAT-NUT-M10",   "너트 M10",           "BOLT",  "EA",    20),
        ("00000003-0000-0000-0001-000000000010", "MAT-PAINT-WH",  "백색 도료",          "PAINT", "L",   8500),
    ]
    for mid, code, name, mtype, unit, price in materials:
        run(conn, f"material:{code}", """
            INSERT INTO material (material_id, material_code, material_name, material_type, unit, standard_unit_price, is_deleted)
            VALUES (:mid, :code, :name, :mtype, :unit, :price, false)
            ON CONFLICT (material_code) DO NOTHING
        """, {"mid": mid, "code": code, "name": name, "mtype": mtype, "unit": unit, "price": price})

    # ── 4. Customer (10개) ────────────────────────────────────────────────────
    print("\n[4] 고객사 10개 생성")
    customers = [
        ("00000004-0000-0000-0001-000000000001", "CUS-001", "한전KPS(주)",        "010-1234-5678", "kim@kps.co.kr"),
        ("00000004-0000-0000-0001-000000000002", "CUS-002", "삼성물산 건설부문",  "010-2345-6789", "lee@samsung.com"),
        ("00000004-0000-0000-0001-000000000003", "CUS-003", "현대건설(주)",       "010-3456-7890", "park@hdec.co.kr"),
        ("00000004-0000-0000-0001-000000000004", "CUS-004", "GS건설",             "010-4567-8901", "choi@gs.co.kr"),
        ("00000004-0000-0000-0001-000000000005", "CUS-005", "대우건설(주)",       "010-5678-9012", "jung@daewoo.co.kr"),
        ("00000004-0000-0000-0001-000000000006", "CUS-006", "롯데건설",           "010-6789-0123", "lim@lotte.co.kr"),
        ("00000004-0000-0000-0001-000000000007", "CUS-007", "포스코건설",         "010-7890-1234", "kang@posco.co.kr"),
        ("00000004-0000-0000-0001-000000000008", "CUS-008", "SK에코플랜트",       "010-8901-2345", "yoon@sk.co.kr"),
        ("00000004-0000-0000-0001-000000000009", "CUS-009", "한화건설",           "010-9012-3456", "oh@hanwha.co.kr"),
        ("00000004-0000-0000-0001-000000000010", "CUS-010", "두산에너빌리티",     "010-0123-4567", "shin@doosan.com"),
    ]
    for cid, code, name, phone, email in customers:
        contact = json.dumps({"phone": phone, "email": email})
        run(conn, f"customer:{code}", """
            INSERT INTO customer (customer_id, customer_code, customer_name, contact_info, is_deleted)
            VALUES (:cid, :code, :name, CAST(:contact AS JSONB), false)
            ON CONFLICT (customer_code) DO NOTHING
        """, {"cid": cid, "code": code, "name": name, "contact": contact})

    # ── 5. PLC Controller (4개) ───────────────────────────────────────────────
    print("\n[5] PLC 컨트롤러 4개 생성")
    plcs = [
        ("00000005-0000-0000-0001-000000000001", "PLC-MASTER-01", "MASTER", "192.168.1.10", "OPC-UA"),
        ("00000005-0000-0000-0001-000000000002", "PLC-SLAVE-01",  "SLAVE",  "192.168.1.11", "Modbus"),
        ("00000005-0000-0000-0001-000000000003", "PLC-SLAVE-02",  "SLAVE",  "192.168.1.12", "Modbus"),
        ("00000005-0000-0000-0001-000000000004", "PLC-SLAVE-03",  "SLAVE",  "192.168.1.13", "MQTT"),
    ]
    for pid, code, ptype, ip, proto in plcs:
        run(conn, f"plc:{code}", """
            INSERT INTO plc_controller (plc_id, plc_code, plc_type, ip_address, protocol, is_active)
            VALUES (:pid, :code, :ptype, :ip, :proto, true)
            ON CONFLICT (plc_code) DO NOTHING
        """, {"pid": pid, "code": code, "ptype": ptype, "ip": ip, "proto": proto})

    # ── 6. Equipment (10개) ───────────────────────────────────────────────────
    print("\n[6] 설비 10개 생성")
    equipment = [
        ("00000006-0000-0000-0001-000000000001", "EQ-FORMING-01",  "렁 성형기 #1",    "FORMING",  "00000005-0000-0000-0001-000000000001", "IDLE"),
        ("00000006-0000-0000-0001-000000000002", "EQ-FORMING-02",  "채널 성형기 #2",  "FORMING",  "00000005-0000-0000-0001-000000000001", "RUNNING"),
        ("00000006-0000-0000-0001-000000000003", "EQ-WELDING-01",  "로봇 용접기 #1",  "WELDING",  "00000005-0000-0000-0001-000000000002", "RUNNING"),
        ("00000006-0000-0000-0001-000000000004", "EQ-WELDING-02",  "로봇 용접기 #2",  "WELDING",  "00000005-0000-0000-0001-000000000002", "IDLE"),
        ("00000006-0000-0000-0001-000000000005", "EQ-CUTTING-01",  "자동 절단기 #1",  "CUTTING",  "00000005-0000-0000-0001-000000000001", "RUNNING"),
        ("00000006-0000-0000-0001-000000000006", "EQ-CUTTING-02",  "자동 절단기 #2",  "CUTTING",  "00000005-0000-0000-0001-000000000003", "MAINTENANCE"),
        ("00000006-0000-0000-0001-000000000007", "EQ-PAINTING-01", "도장 설비 #1",    "PAINTING", "00000005-0000-0000-0001-000000000003", "IDLE"),
        ("00000006-0000-0000-0001-000000000008", "EQ-PACKING-01",  "포장 라인 #1",    "PACKING",  "00000005-0000-0000-0001-000000000004", "RUNNING"),
        ("00000006-0000-0000-0001-000000000009", "EQ-PRESS-01",    "프레스 #1",       "FORMING",  "00000005-0000-0000-0001-000000000004", "IDLE"),
        ("00000006-0000-0000-0001-000000000010", "EQ-GRINDER-01",  "연삭기 #1",       "CUTTING",  "00000005-0000-0000-0001-000000000003", "ERROR"),
    ]
    for eid, code, name, ptype, plc_id, status in equipment:
        run(conn, f"equipment:{code}", """
            INSERT INTO equipment (equipment_id, equipment_code, equipment_name, process_type, plc_id, status, is_deleted)
            VALUES (:eid, :code, :name, :ptype, :plc_id, :status, false)
            ON CONFLICT (equipment_code) DO NOTHING
        """, {"eid": eid, "code": code, "name": name, "ptype": ptype, "plc_id": plc_id, "status": status})

    # ── 7. Quality Standard (10개) ────────────────────────────────────────────
    print("\n[7] 품질 기준 10개 생성")
    standards = [
        ("00000007-0000-0000-0001-000000000001", "QS-FORMING-001", "LADDER_TRAY",   "FORMING",
         {"thickness_tolerance_mm": 0.2, "length_tolerance_mm": 1.0, "angle_tolerance_deg": 0.5}),
        ("00000007-0000-0000-0001-000000000002", "QS-WELDING-001", "LADDER_TRAY",   "WELDING",
         {"bead_width_min_mm": 5.0, "bead_width_max_mm": 9.0, "porosity_allowed": False}),
        ("00000007-0000-0000-0001-000000000003", "QS-FINAL-001",   "LADDER_TRAY",   "FINAL",
         {"surface_defect_max": 0, "dimension_tolerance_mm": 1.5, "paint_adhesion_min_mpa": 3.0}),
        ("00000007-0000-0000-0001-000000000004", "QS-FORMING-002", "CABLE_TRAY",    "FORMING",
         {"thickness_tolerance_mm": 0.3, "length_tolerance_mm": 1.5, "angle_tolerance_deg": 0.8}),
        ("00000007-0000-0000-0001-000000000005", "QS-WELDING-002", "CABLE_TRAY",    "WELDING",
         {"bead_width_min_mm": 4.0, "bead_width_max_mm": 8.0, "porosity_allowed": False}),
        ("00000007-0000-0000-0001-000000000006", "QS-CUTTING-001", "LADDER_TRAY",   "CUTTING",
         {"length_tolerance_mm": 0.5, "squareness_tolerance_deg": 0.3, "burr_height_max_mm": 0.1}),
        ("00000007-0000-0000-0001-000000000007", "QS-PAINTING-001","LADDER_TRAY",   "PAINTING",
         {"dry_film_thickness_min_um": 60, "dry_film_thickness_max_um": 100, "adhesion_grade_max": 1}),
        ("00000007-0000-0000-0001-000000000008", "QS-INCOMING-001","SS400",          "INCOMING",
         {"thickness_tolerance_mm": 0.1, "tensile_strength_min_mpa": 400, "yield_strength_min_mpa": 245}),
        ("00000007-0000-0000-0001-000000000009", "QS-FINAL-002",   "CABLE_TRAY",    "FINAL",
         {"surface_defect_max": 0, "dimension_tolerance_mm": 2.0, "paint_adhesion_min_mpa": 2.5}),
        ("00000007-0000-0000-0001-000000000010", "QS-PACKING-001", "LADDER_TRAY",   "PACKING",
         {"bundle_qty": 10, "label_required": True, "protection_layer_required": True}),
    ]
    for qid, code, ptype, proc, criteria in standards:
        run(conn, f"quality_std:{code}", """
            INSERT INTO quality_standard (qs_id, qs_code, product_type, process_type, criteria, is_active)
            VALUES (:qid, :code, :ptype, :proc, CAST(:criteria AS JSONB), true)
            ON CONFLICT (qs_code) DO NOTHING
        """, {"qid": qid, "code": code, "ptype": ptype, "proc": proc,
              "criteria": json.dumps(criteria)})

    # ── 8. Orders (10건) ──────────────────────────────────────────────────────
    print("\n[8] 수주 10건 생성")
    orders = [
        ("00000008-0000-0000-0001-000000000001", "ORD-2026-000001", "00000004-0000-0000-0001-000000000001", "RECEIVED",    "LADDER_TRAY", 100, "2026-08-01",
         {"width_mm": 200, "thickness_mm": 2.0, "material": "SS400", "length_mm": 3000}),
        ("00000008-0000-0000-0001-000000000002", "ORD-2026-000002", "00000004-0000-0000-0001-000000000002", "CONFIRMED",   "CABLE_TRAY",   50, "2026-07-15",
         {"width_mm": 300, "thickness_mm": 2.0, "material": "SS400", "length_mm": 2400}),
        ("00000008-0000-0000-0001-000000000003", "ORD-2026-000003", "00000004-0000-0000-0001-000000000003", "IN_PROGRESS",  "LADDER_TRAY", 200, "2026-07-30",
         {"width_mm": 150, "thickness_mm": 1.5, "material": "SS400", "length_mm": 3000}),
        ("00000008-0000-0000-0001-000000000004", "ORD-2026-000004", "00000004-0000-0000-0001-000000000004", "QUOTING",     "CABLE_TRAY",   80, "2026-08-15",
         {"width_mm": 400, "thickness_mm": 3.0, "material": "SS400", "length_mm": 3000}),
        ("00000008-0000-0000-0001-000000000005", "ORD-2026-000005", "00000004-0000-0000-0001-000000000005", "RECEIVED",    "LADDER_TRAY", 150, "2026-09-01",
         {"width_mm": 200, "thickness_mm": 2.0, "material": "SS400", "length_mm": 6000}),
        ("00000008-0000-0000-0001-000000000006", "ORD-2026-000006", "00000004-0000-0000-0001-000000000006", "SHIPPED",     "CABLE_TRAY",  120, "2026-06-30",
         {"width_mm": 300, "thickness_mm": 2.0, "material": "SS400", "length_mm": 3600}),
        ("00000008-0000-0000-0001-000000000007", "ORD-2026-000007", "00000004-0000-0000-0001-000000000007", "CONFIRMED",   "LADDER_TRAY",  60, "2026-08-20",
         {"width_mm": 250, "thickness_mm": 2.5, "material": "SS400", "length_mm": 3000}),
        ("00000008-0000-0000-0001-000000000008", "ORD-2026-000008", "00000004-0000-0000-0001-000000000008", "IN_PROGRESS",  "CABLE_TRAY",   90, "2026-07-20",
         {"width_mm": 200, "thickness_mm": 2.0, "material": "SS400", "length_mm": 2400}),
        ("00000008-0000-0000-0001-000000000009", "ORD-2026-000009", "00000004-0000-0000-0001-000000000009", "RECEIVED",    "LADDER_TRAY",  40, "2026-09-15",
         {"width_mm": 150, "thickness_mm": 1.5, "material": "SS400", "length_mm": 4500}),
        ("00000008-0000-0000-0001-000000000010", "ORD-2026-000010", "00000004-0000-0000-0001-000000000010", "QUOTING",     "CABLE_TRAY",   70, "2026-08-31",
         {"width_mm": 350, "thickness_mm": 3.0, "material": "SS400", "length_mm": 3000}),
    ]
    for oid, order_no, cid, status, ptype, qty, delivery, spec in orders:
        run(conn, f"order:{order_no}", f"""
            INSERT INTO "order" (order_id, order_no, customer_id, status, product_type, product_spec, quantity, requested_delivery_date, is_deleted)
            VALUES (:oid, :order_no, :cid, :status, :ptype, CAST(:spec AS JSONB), :qty, :delivery, false)
            ON CONFLICT (order_no) DO NOTHING
        """, {"oid": oid, "order_no": order_no, "cid": cid, "status": status,
              "ptype": ptype, "qty": qty, "delivery": delivery,
              "spec": json.dumps(spec)})

    # ── 9. Quotes (10건) ──────────────────────────────────────────────────────
    print("\n[9] 견적 10건 생성")
    quotes = [
        ("00000009-0000-0000-0001-000000000001", "QTE-2026-000001", "00000008-0000-0000-0001-000000000001",
         1523400, 980000, 543400, 0.91, 5, "AUTO",
         {"forming": 180000, "welding": 240000, "cutting": 123400},
         [{"feature": "total_length_mm", "impact": 0.35, "value": 3000},
          {"feature": "bend_count",      "impact": 0.22, "value": 4}]),
        ("00000009-0000-0000-0001-000000000002", "QTE-2026-000002", "00000008-0000-0000-0001-000000000002",
         892000,  560000, 332000, 0.88, 4, "APPROVED",
         {"forming": 110000, "welding": 150000, "cutting": 72000},
         [{"feature": "width_mm",        "impact": 0.28, "value": 300},
          {"feature": "total_length_mm", "impact": 0.32, "value": 2400}]),
        ("00000009-0000-0000-0001-000000000003", "QTE-2026-000003", "00000008-0000-0000-0001-000000000003",
         2845600, 1820000, 1025600, 0.93, 7, "AUTO",
         {"forming": 340000, "welding": 480000, "cutting": 205600},
         [{"feature": "quantity",        "impact": 0.41, "value": 200},
          {"feature": "total_length_mm", "impact": 0.29, "value": 3000}]),
        ("00000009-0000-0000-0001-000000000004", "QTE-2026-000004", "00000008-0000-0000-0001-000000000004",
         1420000, 920000, 500000, 0.85, 6, "AUTO",
         {"forming": 165000, "welding": 220000, "cutting": 115000},
         [{"feature": "thickness_mm",    "impact": 0.31, "value": 3.0},
          {"feature": "width_mm",        "impact": 0.25, "value": 400}]),
        ("00000009-0000-0000-0001-000000000005", "QTE-2026-000005", "00000008-0000-0000-0001-000000000005",
         3120000, 1980000, 1140000, 0.90, 8, "AUTO",
         {"forming": 380000, "welding": 510000, "cutting": 250000},
         [{"feature": "length_mm",       "impact": 0.38, "value": 6000},
          {"feature": "quantity",        "impact": 0.27, "value": 150}]),
        ("00000009-0000-0000-0001-000000000006", "QTE-2026-000006", "00000008-0000-0000-0001-000000000006",
         1986000, 1280000, 706000, 0.92, 5, "APPROVED",
         {"forming": 233000, "welding": 310000, "cutting": 163000},
         [{"feature": "quantity",        "impact": 0.33, "value": 120},
          {"feature": "width_mm",        "impact": 0.26, "value": 300}]),
        ("00000009-0000-0000-0001-000000000007", "QTE-2026-000007", "00000008-0000-0000-0001-000000000007",
         1050000, 672000, 378000, 0.87, 4, "AUTO",
         {"forming": 125000, "welding": 168000, "cutting": 85000},
         [{"feature": "thickness_mm",    "impact": 0.29, "value": 2.5},
          {"feature": "bend_count",      "impact": 0.24, "value": 5}]),
        ("00000009-0000-0000-0001-000000000008", "QTE-2026-000008", "00000008-0000-0000-0001-000000000008",
         1490000, 960000, 530000, 0.89, 5, "AUTO",
         {"forming": 175000, "welding": 235000, "cutting": 120000},
         [{"feature": "total_length_mm", "impact": 0.30, "value": 2400},
          {"feature": "quantity",        "impact": 0.28, "value": 90}]),
        ("00000009-0000-0000-0001-000000000009", "QTE-2026-000009", "00000008-0000-0000-0001-000000000009",
         710000,  456000, 254000, 0.84, 4, "AUTO",
         {"forming": 84000, "welding": 113000, "cutting": 57000},
         [{"feature": "length_mm",       "impact": 0.27, "value": 4500},
          {"feature": "quantity",        "impact": 0.22, "value": 40}]),
        ("00000009-0000-0000-0001-000000000010", "QTE-2026-000010", "00000008-0000-0000-0001-000000000010",
         1260000, 812000, 448000, 0.86, 5, "AUTO",
         {"forming": 148000, "welding": 198000, "cutting": 102000},
         [{"feature": "thickness_mm",    "impact": 0.32, "value": 3.0},
          {"feature": "width_mm",        "impact": 0.23, "value": 350}]),
    ]
    for qid, quote_no, oid, total, mat, proc, conf, lead, status, pbreak, shap_feat in quotes:
        run(conn, f"quote:{quote_no}", """
            INSERT INTO quote (quote_id, quote_no, order_id, total_amount, material_cost, process_cost,
                               process_cost_breakdown, shap_explanation, confidence_score, estimated_lead_time_days, status)
            VALUES (:qid, :quote_no, :oid, :total, :mat, :proc,
                    CAST(:pbreak AS JSONB), CAST(:shap AS JSONB),
                    :conf, :lead, :status)
            ON CONFLICT (quote_no) DO NOTHING
        """, {
            "qid": qid, "quote_no": quote_no, "oid": oid,
            "total": total, "mat": mat, "proc": proc,
            "pbreak": json.dumps(pbreak),
            "shap": json.dumps({"top_features": shap_feat}),
            "conf": conf, "lead": lead, "status": status,
        })

    # ── 10. Receiving LOT (10건) ──────────────────────────────────────────────
    print("\n[10] 입고 LOT 10건 생성")
    lots = [
        ("00000010-0000-0000-0001-000000000001", "LOT-2026-0601-001", "00000002-0000-0000-0001-000000000001", "MAT-SS400-2T",  "2026-06-01", 50.0,  235.5, 2.0, "PASS", "A-03-02"),
        ("00000010-0000-0000-0001-000000000002", "LOT-2026-0601-002", "00000002-0000-0000-0001-000000000002", "MAT-SS400-3T",  "2026-06-01", 30.0,  212.4, 3.0, "PASS", "A-03-03"),
        ("00000010-0000-0000-0001-000000000003", "LOT-2026-0602-001", "00000002-0000-0000-0001-000000000003", "MAT-WIRE-08",   "2026-06-02", 100.0,  None, None, "PASS", "B-01-01"),
        ("00000010-0000-0000-0001-000000000004", "LOT-2026-0602-002", "00000002-0000-0000-0001-000000000001", "MAT-SS400-2T",  "2026-06-02", 80.0,  376.8, 2.0, "PENDING","A-04-01"),
        ("00000010-0000-0000-0001-000000000005", "LOT-2026-0603-001", "00000002-0000-0000-0001-000000000004", "MAT-SS400-1.5T","2026-06-03", 60.0,  211.5, 1.5, "PASS", "A-02-05"),
        ("00000010-0000-0000-0001-000000000006", "LOT-2026-0603-002", "00000002-0000-0000-0001-000000000005", "MAT-SS400-3T",  "2026-06-03", 25.0,  176.9, 3.0, "FAIL", "A-05-01"),
        ("00000010-0000-0000-0001-000000000007", "LOT-2026-0603-003", "00000002-0000-0000-0001-000000000006", "MAT-WIRE-12",   "2026-06-03", 150.0,  None, None, "PASS", "B-01-02"),
        ("00000010-0000-0000-0001-000000000008", "LOT-2026-0603-004", "00000002-0000-0000-0001-000000000007", "MAT-BOLT-M10",  "2026-06-03", 2000.0, None, None, "PASS", "C-01-01"),
        ("00000010-0000-0000-0001-000000000009", "LOT-2026-0603-005", "00000002-0000-0000-0001-000000000008", "MAT-PAINT-GY",  "2026-06-03", 40.0,   None, None, "PENDING","D-01-01"),
        ("00000010-0000-0000-0001-000000000010", "LOT-2026-0603-006", "00000002-0000-0000-0001-000000000009", "MAT-SS400-2T",  "2026-06-03", 45.0,  211.8, 2.0, "PASS", "A-03-04"),
    ]
    for lid, lot_no, sid, mcode, rdate, qty, wkg, thick, result, loc in lots:
        run(conn, f"lot:{lot_no}", """
            INSERT INTO receiving_lot (lot_id, lot_no, supplier_id, material_code, received_date,
                                       quantity, weight_kg, thickness_mm, inspection_result, storage_location, is_deleted)
            VALUES (:lid, :lot_no, :sid, :mcode, :rdate, :qty, :wkg, :thick, :result, :loc, false)
            ON CONFLICT (lot_no) DO NOTHING
        """, {"lid": lid, "lot_no": lot_no, "sid": sid, "mcode": mcode,
              "rdate": rdate, "qty": qty, "wkg": wkg, "thick": thick,
              "result": result, "loc": loc})

    conn.execute(text("COMMIT"))

print("\n" + "="*60)
print("Seed 완료! (각 엔티티 10개)")
print("="*60)
print("\n[테스트 계정]")
for uid, username, role, dept, name in users:
    print(f"  {username:12s} / password1234  ({role} - {name})")
print("\n[데이터 현황]")
print("  사용자: 10명 | 공급처: 10개 | 원자재: 10개 | 고객사: 10개")
print("  설비: 10개   | 품질기준: 10개 | 수주: 10건 | 견적: 10건")
print("  입고LOT: 10건")
print("\n[API] http://127.0.0.1:8001/docs")
