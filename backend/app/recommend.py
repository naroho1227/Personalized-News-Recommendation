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

    # 최소 3% 보장 — 재정규화 후에도 floor가 유지될 때까지 반복
    normalized = raw
    for _ in range(10):
        floored = {c: max(normalized[c], MIN_RATIO) for c in CATEGORIES}
        s = sum(floored.values())
        normalized = {c: floored[c] / s for c in CATEGORIES}
        if min(normalized.values()) >= MIN_RATIO - 1e-9:
            break

    return normalized


def update_score_on_click(db: Session, user: User, clicked_category: str) -> None:
    scores = get_scores(user)
    ratios = softmax_ratios(scores)

    current_ratio = ratios[clicked_category]
    decay = max(0.0, 1.0 - current_ratio / SATURATION_RATIO)
    scores[clicked_category] += decay

    set_scores(user, scores)
    db.commit()


def get_featured(db: Session, user_id: int, clicked_ids: list[int]) -> dict:
    """
    상단 영역용 추천
    - top    : 추천 비율 1위 카테고리에서 1건
    - others : 나머지 6개 카테고리에서 각 1건 (균등)
    반환값에 used_ids(상단에 노출된 기사 id 목록) 포함
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"top": None, "top_ratio": 0.0, "others": [], "used_ids": []}

    scores  = get_scores(user)
    ratios  = softmax_ratios(scores)
    top_cat = max(ratios, key=ratios.get)
    other_cats = [c for c in CATEGORIES if c != top_cat]

    used_ids = list(clicked_ids)

    # 1위 카테고리 기사 1건
    top_q = db.query(News).filter(News.category == top_cat)
    if used_ids:
        top_q = top_q.filter(News.id.notin_(used_ids))
    top_article = top_q.order_by(News.created_at.desc()).first()
    if top_article:
        used_ids.append(top_article.id)

    # 나머지 6개 카테고리 각 1건
    other_news = []
    for cat in other_cats:
        q = db.query(News).filter(News.category == cat)
        if used_ids:
            q = q.filter(News.id.notin_(used_ids))
        article = q.order_by(News.created_at.desc()).first()
        if article:
            used_ids.append(article.id)
            other_news.append(article)

    return {
        "top": top_article,
        "top_ratio": round(ratios[top_cat] * 100, 1),
        "others": other_news,
        "used_ids": used_ids,
    }


def get_recommendations(db: Session, user_id: int, limit: int = 13,
                        exclude_ids: list[int] | None = None) -> list[News]:
    """
    하단 알고리즘 기반 추천 (기본 13건)
    exclude_ids : 상단에서 사용한 id + 클릭 이력 id
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    clicked_ids = [
        log.news_id
        for log in db.query(UserLog)
        .filter(UserLog.user_id == user_id, UserLog.action == "click")
        .all()
    ]

    all_exclude = list(set(clicked_ids + (exclude_ids or [])))

    scores    = get_scores(user)
    ratios    = softmax_ratios(scores)

    raw_counts = {c: ratios[c] * limit for c in CATEGORIES}
    counts: dict[str, int] = {c: int(raw_counts[c]) for c in CATEGORIES}

    shortage   = limit - sum(counts.values())
    remainders = sorted(CATEGORIES, key=lambda c: raw_counts[c] - counts[c], reverse=True)
    for i in range(shortage):
        counts[remainders[i]] += 1

    result: list[News] = []
    for category, n in counts.items():
        if n <= 0:
            continue
        q = db.query(News).filter(News.category == category)
        if all_exclude:
            q = q.filter(News.id.notin_(all_exclude))
        result.extend(q.order_by(News.created_at.desc()).limit(n).all())

    return result
