from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

from .database import engine, Base, SessionLocal
from .models import User, UserLog
from .recommend import get_recommendations, update_score, get_ratios, CATEGORIES

SECRET_KEY = "newspick-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

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


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except (JWTError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="인증이 필요합니다.")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="사용자를 찾을 수 없습니다.")
    return user


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    nickname: str
    interest: str


class LogRequest(BaseModel):
    news_url: str
    news_category: str
    action: str


@app.get("/")
def root():
    return {"message": "NewsPick API"}


@app.post("/auth/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if body.interest not in CATEGORIES:
        raise HTTPException(status_code=400, detail="유효하지 않은 카테고리입니다.")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")

    scores = {cat: 1.0 for cat in CATEGORIES}
    scores[body.interest] = 1.5

    user = User(
        email=body.email,
        password=hash_password(body.password),
        nickname=body.nickname,
        score_general=scores["general"],
        score_technology=scores["technology"],
        score_business=scores["business"],
        score_sports=scores["sports"],
        score_science=scores["science"],
        score_health=scores["health"],
        score_entertainment=scores["entertainment"],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "가입이 완료되었습니다."}


@app.post("/auth/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form.username).first()
    if not user or not verify_password(form.password, user.password):
        raise HTTPException(status_code=400, detail="이메일 또는 비밀번호가 올바르지 않습니다.")
    token = create_token(user.id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "nickname": user.nickname,
    }


@app.get("/recommend")
def recommend_news(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    articles = get_recommendations(db, current_user.id)
    if not articles:
        raise HTTPException(status_code=404, detail="추천 기사를 불러올 수 없습니다.")
    return articles


@app.post("/log")
def save_log(log: LogRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if log.action not in ("view", "click"):
        raise HTTPException(status_code=400, detail="유효하지 않은 액션입니다.")
    if log.news_category not in CATEGORIES:
        raise HTTPException(status_code=400, detail="유효하지 않은 카테고리입니다.")

    new_log = UserLog(
        user_id=current_user.id,
        news_url=log.news_url,
        news_category=log.news_category,
        action=log.action,
    )
    db.add(new_log)

    if log.action == "click":
        update_score(db, current_user, log.news_category)

    db.commit()
    return {"status": "ok"}


@app.get("/stats")
def get_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ratios = get_ratios(current_user)
    return [
        {"name": cat, "ratio": round(ratio * 100, 2)}
        for cat, ratio in ratios.items()
    ]


frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frountend")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
