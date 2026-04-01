from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .database import engine, Base, SessionLocal
from .models import News, UserLog
from .recommend import get_recommendations

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class LogRequest(BaseModel):
    user_id: int
    news_id: int
    action: str

@app.get("/")
def root():
    return {"message": "News Recommendation API is running"}

@app.get("/recommend/{user_id}")
def recommend_news(user_id: int, db: Session = Depends(get_db)):
    news = get_recommendations(db, user_id)
    return [{"id": n.id, "title": n.title, "category": n.category,
            "description": n.description, "url": n.url} for n in news]

@app.post("/log")
def save_log(log: LogRequest, db: Session = Depends(get_db)):
    new_log = UserLog(user_id=log.user_id, news_id=log.news_id, action=log.action)
    db.add(new_log)
    db.commit()
    return {"status": "success"}