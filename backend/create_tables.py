"""
alembic 대신 SQLAlchemy create_all로 초기 테이블 생성
Windows 인코딩 이슈 우회용
"""
import os
os.environ["PGPASSFILE"] = "NUL"  # Windows /dev/null — pgpass 파일 무시

from sqlalchemy import create_engine, text

# 모든 모델 import (Base.metadata 등록)
from app.database import Base
import app.domains.system.models
import app.domains.order.models
import app.domains.cad.models
import app.domains.receiving.models
import app.domains.production.models
import app.domains.quality.models
import app.domains.shipping.models
import app.domains.equipment.models

DB_URL = "postgresql+pg8000://buyoung:password@localhost:5432/buyoung_mes"

engine = create_engine(DB_URL, echo=True)

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    conn.commit()

Base.metadata.create_all(engine)
print(f"\n✅ 테이블 생성 완료: {len(Base.metadata.tables)}개")
for t in sorted(Base.metadata.tables.keys()):
    print(f"  - {t}")
