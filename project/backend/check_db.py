import sqlite3

DB_PATH = "C:/Users/yhw76/project/news.db" 

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cur.fetchall()
print("DB 테이블 목록:", tables)

cur.execute("SELECT title, content, category, created_at FROM news LIMIT 10;")
rows = cur.fetchall()

print("\n뉴스 데이터 샘플:")
for i, row in enumerate(rows, start=1):
    title, content, category, created_at = row
    print(f"{i}. [{category}] {title} - {content} ({created_at})")

conn.close()
