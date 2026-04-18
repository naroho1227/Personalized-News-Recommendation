from backend.app.database import engine, Base
from backend.app import models
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT current_database(), inet_server_addr(), inet_server_port()"))
    row = result.fetchone()
    print("현재 DB:", row[0])
    print("서버 주소:", row[1])
    print("서버 포트:", row[2])

    result2 = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
    tables = result2.fetchall()
    print("테이블 목록:", tables)