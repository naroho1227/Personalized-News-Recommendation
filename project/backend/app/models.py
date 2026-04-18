from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    nickname      = Column(String, nullable=False)
    interest      = Column(String, nullable=False)   # 초기 관심사 (단일)

    # 카테고리별 점수 (초기값: 관심사 1.5, 나머지 1.0)
    score_general       = Column(Float, default=1.0, nullable=False)
    score_technology    = Column(Float, default=1.0, nullable=False)
    score_business      = Column(Float, default=1.0, nullable=False)
    score_sports        = Column(Float, default=1.0, nullable=False)
    score_science       = Column(Float, default=1.0, nullable=False)
    score_health        = Column(Float, default=1.0, nullable=False)
    score_entertainment = Column(Float, default=1.0, nullable=False)


class News(Base):
    __tablename__ = "news"
    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, index=True, nullable=False)
    content     = Column(Text)
    description = Column(Text)
    url         = Column(String)
    category    = Column(String, index=True, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow)


class UserLog(Base):
    __tablename__ = "user_logs"
    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    news_id   = Column(Integer, ForeignKey("news.id"), nullable=False)
    action    = Column(String, nullable=False)   # "view" | "click"
    timestamp = Column(DateTime, default=datetime.utcnow)
