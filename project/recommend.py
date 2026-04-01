
from app.database import SessionLocal
from app.models import User, News, UserLog

def get_user_interest(user_id: int) -> str | None:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        return user.interest if user else None
    finally:
        db.close()

def filter_news_by_category(category: str) -> list:
    db = SessionLocal()
    try:
        return db.query(News)\
                .filter(News.category == category)\
                .order_by(News.created_at.desc())\
                .all()
    finally:
        db.close()

def get_category_scores(user_id: int) -> dict:
    db = SessionLocal()
    try:
        logs = db.query(UserLog).filter(UserLog.user_id == user_id).all()
        scores = {}
        for log in logs:
            news = db.query(News).filter(News.id == log.news_id).first()
            if not news:
                continue
            point = 2 if log.action == "click" else 1
            scores[news.category] = scores.get(news.category, 0) + point
        return scores
    finally:
        db.close()