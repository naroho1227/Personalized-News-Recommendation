from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    interest = Column(String)

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    category = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserLog(Base):
    __tablename__ = "user_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    news_id = Column(Integer, ForeignKey("news.id"))
    action = Column(String)
