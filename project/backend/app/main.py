import os
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from jose import JWTError, jwt
from passlib.context import CryptContext

from .database import engine, Base, SessionLocal
from .models import News, User, UserLog
from .recommend import get_recommendations, softmax_ratios, get_scores, update_score_on_click, CATEGORIES

SECRET_KEY      = os.getenv("SECRET_KEY", "change-this-secret-in-production")
ALGORITHM       = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()
VALID_CATEGORIES = CATEGORIES
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frountend"

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Base.metadata.create_all(bind=engine)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> int:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: str
    interest: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LogRequest(BaseModel):
    news_id: int
    action: str

@app.get("/")
def serve_frontend():
    return FileResponse(str(FRONTEND_DIR / "index.html"))

@app.get("/news_list")
def serve_news_list():
    return FileResponse(str(FRONTEND_DIR / "news_list.html"))

@app.get("/api")
def root():
    return {"message": "News Recommendation API is running"}

@app.post("/auth/register", status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if body.interest not in VALID_CATEGORIES:
        raise HTTPException(400, detail=f"interest must be one of: {VALID_CATEGORIES}")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(409, detail="Email already registered")
    score_init = {f"score_{c}": (1.5 if c == body.interest else 1.0) for c in VALID_CATEGORIES}
    user = User(email=body.email, password_hash=pwd_context.hash(body.password), nickname=body.nickname, interest=body.interest, **score_init)
    db.add(user); db.commit(); db.refresh(user)
    return {"id": user.id, "email": user.email, "nickname": user.nickname, "interest": user.interest}

@app.post("/auth/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not pwd_context.verify(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user_id": user.id, "nickname": user.nickname}

@app.get("/recommend/{user_id}")
def recommend_news(user_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    news = get_recommendations(db, user_id)
    return [{"id": n.id, "title": n.title, "category": n.category, "description": n.description, "url": n.url} for n in news]

@app.post("/log")
def save_log(log: LogRequest, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    user = db.query(User).filter(User.id == current_user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    news = db.query(News).filter(News.id == log.news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    if log.action not in ("view", "click"):
        raise HTTPException(status_code=400, detail="action must be 'view' or 'click'")
    new_log = UserLog(user_id=current_user_id, news_id=log.news_id, action=log.action)
    db.add(new_log); db.commit()
    if log.action == "click":
        update_score_on_click(db, user, news.category)
    return {"status": "success"}

@app.get("/stats/{user_id}")
def get_stats(user_id: int, db: Session = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    if current_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    scores = get_scores(user)
    ratios = softmax_ratios(scores)
    return {"user_id": user_id, "stats": [{"category": c, "score": round(scores[c], 4), "ratio": round(ratios[c] * 100, 2)} for c in CATEGORIES]}
