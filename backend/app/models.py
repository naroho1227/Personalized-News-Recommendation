from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    nickname = Column(String, nullable=False)
    score_general = Column(Float, default=1.0)
    score_technology = Column(Float, default=1.0)
    score_business = Column(Float, default=1.0)
    score_sports = Column(Float, default=1.0)
    score_science = Column(Float, default=1.0)
    score_health = Column(Float, default=1.0)
    score_entertainment = Column(Float, default=1.0)


class UserLog(Base):
    __tablename__ = "user_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    news_url = Column(String, nullable=False)
    news_category = Column(String, nullable=False)
    action = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
