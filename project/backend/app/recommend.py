import math
from sqlalchemy.orm import Session
from .models import News, User, UserLog

CATEGORIES = [
    "general", "technology", "business",
    "sports", "science", "health", "entertainment",
]

SATURATION_RATIO = 0.50
MIN_RATIO        = 0.03
SCORE_ATTR       = {c: f"score_{c}" for c in CATEGORIES}


def get_scores(user: User) -> dict[str, float]:
    return {c: getattr(user, SCORE_ATTR[c]) for c in CATEGORIES}


def set_scores(user: User, scores: dict[str, float]) -> None:
    for c, v in scores.items():
        setattr(user, SCORE_ATTR[c], v)


def softmax_ratios(scores: dict[str, float]) -> dict[str, float]:
    vals = list(scores.values())
    max_v = max(vals)
    exps = {c: math.exp(scores[c] - max_v) for c in CATEGORIES}
    total = sum(exps.values())
    raw = {c: exps[c] / total for c in CATEGORIES}

    # 최소 3% 보장
    floor = MIN_RATIO
    floored = {c: max(raw[c], floor) for c in CATEGORIES}
    s = sum(floored.values())
    return {c: floored[c] / s for c in CATEGORIES}


def update_score_on_click(db: Session, user: User, clicked_category: str) -> None:
    scores = get_scores(user)
    ratios = softmax_ratios(scores)

    current_ratio = ratios[clicked_category]
    decay = max(0.0, 1.0 - current_ratio / SATURATION_RATIO)
    scores[clicked_category] += decay

    set_scores(user, scores)
    db.commit()


def get_recommendations(db: Session, user_id: int, limit: int = 20) -> list[News]:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    clicked_ids = [
        log.news_id
        for log in db.query(UserLog)
        .filter(UserLog.user_id == user_id, UserLog.action == "click")
        .all()
    ]

    scores = get_scores(user)
    ratios = softmax_ratios(scores)

    raw_counts = {c: ratios[c] * limit for c in CATEGORIES}
    counts: dict[str, int] = {c: int(raw_counts[c]) for c in CATEGORIES}

    shortage = limit - sum(counts.values())
    remainders = sorted(CATEGORIES, key=lambda c: raw_counts[c] - counts[c], reverse=True)
    for i in range(shortage):
        counts[remainders[i]] += 1

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
