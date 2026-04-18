import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import SessionLocal
from backend.app.models import News, User, UserLog


def check_db():
    db = SessionLocal()


    news_count = db.query(News).count()
    user_count = db.query(User).count()
    log_count = db.query(UserLog).count()

    print(f"=== DB 현황 ===")
    print(f"뉴스: {news_count}건 / 유저: {user_count}명 / 로그: {log_count}건")

    print(f"\n=== 뉴스 샘플 (최신 10건) ===")
    for i, n in enumerate(db.query(News).order_by(News.created_at.desc()).limit(10).all(), 1):
        print(f"{i}. [{n.category}] {n.title} ({n.created_at})")

    print(f"\n=== 유저 목록 ===")
    for u in db.query(User).all():
        print(f"  id={u.id}  interest={u.interest}")

    db.close()


if __name__ == "__main__":
    check_db()
