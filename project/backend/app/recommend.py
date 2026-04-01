from sqlalchemy.orm import Session
from .models import News, User

def get_recommendations(db: Session, user_id: int, limit=5):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    return db.query(News)\
            .filter(News.category == user.interest)\
            .order_by(News.created_at.desc())\
            .limit(limit)\
            .all()
