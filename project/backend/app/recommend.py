import math
from sqlalchemy.orm import Session
from .models import News, User, UserLog

CATEGORIES = [
    "general", "technology", "business",
    "sports", "science", "health", "entertainment",
]

SATURATION_RATIO = 0.50   # 포화 비율 50%
MIN_RATIO        = 0.03   # 최소 노출 비율 3%
SCORE_ATTR       = {c: f"score_{c}" for c in CATEGORIES}


# ── 점수 헬퍼 ──────────────────────────────────────────────
def get_scores(user: User) -> dict[str, float]:
    return {c: getattr(user, SCORE_ATTR[c]) for c in CATEGORIES}


def set_scores(user: User, scores: dict[str, float]) -> None:
    for c, v in scores.items():
        setattr(user, SCORE_ATTR[c], v)


# ── Softmax → 최소 비율 보장 ───────────────────────────────
def softmax_ratios(scores: dict[str, float]) -> dict[str, float]:
    vals = list(scores.values())
    max_v = max(vals)
    exps = {c: math.exp(scores[c] - max_v) for c in CATEGORIES}   # 수치 안정성
    total = sum(exps.values())
    raw = {c: exps[c] / total for c in CATEGORIES}

    # 최소 3% 보장
    floor = MIN_RATIO
    floored = {c: max(raw[c], floor) for c in CATEGORIES}
    s = sum(floored.values())
    return {c: floored[c] / s for c in CATEGORIES}


# ── 클릭 시 점수 업데이트 (감쇠 계수) ─────────────────────
def update_score_on_click(db: Session, user: User, clicked_category: str) -> None:
    scores = get_scores(user)
    ratios = softmax_ratios(scores)

    current_ratio = ratios[clicked_category]
    decay = max(0.0, 1.0 - current_ratio / SATURATION_RATIO)   # 감쇠 계수
    scores[clicked_category] += decay

    set_scores(user, scores)
    db.commit()


# ── 추천 알고리즘 ──────────────────────────────────────────
def get_recommendations(db: Session, user_id: int, limit: int = 20) -> list[News]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    # 이미 클릭한 기사 ID 수집
    clicked_ids = [
        log.news_id
        for log in db.query(UserLog)
        .filter(UserLog.user_id == user_id, UserLog.action == "click")
        .all()
    ]

    scores = get_scores(user)
    ratios = softmax_ratios(scores)

    # 카테고리별 할당 건수 계산 (합계 = limit)
    raw_counts = {c: ratios[c] * limit for c in CATEGORIES}
    counts: dict[str, int] = {c: int(raw_counts[c]) for c in CATEGORIES}

    # 반올림 오차로 부족한 건수를 소수점 내림차순으로 채움
    shortage = limit - sum(counts.values())
    remainders = sorted(CATEGORIES, key=lambda c: raw_counts[c] - counts[c], reverse=True)
    for i in range(shortage):
        counts[remainders[i]] += 1

    # 카테고리별 뉴스 조회
    result: list[News] = []
    for category, n in counts.items():
        if n <= 0:
            continue
        query = (
            db.query(News)
            .filter(News.category == category)
        )
        if clicked_ids:
            query = query.filter(News.id.notin_(clicked_ids))
        articles = query.order_by(News.created_at.desc()).limit(n).all()
        result.extend(articles)

    return result
