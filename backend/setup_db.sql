-- Buyoung MES DB 초기 셋업
-- 실행: psql -U postgres -f setup_db.sql

-- 1. 사용자 생성 (이미 있으면 무시)
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'buyoung') THEN
    CREATE ROLE buyoung WITH LOGIN PASSWORD 'password';
  END IF;
END
$$;

-- 2. 데이터베이스 생성 (이미 있으면 무시)
SELECT 'CREATE DATABASE buyoung_mes OWNER buyoung'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'buyoung_mes')\gexec

-- 3. 권한 부여
GRANT ALL PRIVILEGES ON DATABASE buyoung_mes TO buyoung;

\connect buyoung_mes

-- 4. Extension 설치
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- 5. buyoung 사용자에게 스키마 권한 부여
GRANT ALL ON SCHEMA public TO buyoung;

\echo '✅ DB 셋업 완료!'
