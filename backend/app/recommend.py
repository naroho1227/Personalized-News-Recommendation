import math
import random
import sys
import os
from sqlalchemy.orm import Session
from .models import User, UserLog

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "crawler"))
from rss_collector import fetch_rss

CATEGORIES = ["general", "technology", "business", "sports", "science", "health", "entertainment"]

SATURATION = 0.5


def get_scores(user: User) -> dict:
    return {
        "general":       user.score_general,
        "technology":    user.score_technology,
        "business":      user.score_business,
        "sports":        user.score_sports,
        "science":       user.score_science,
        "health":        user.score_health,
        "entertainment": user.score_entertainment,
    }


def softmax(scores: dict) -> dict:
    values = list(scores.values())
    max_v = max(values)
    exps = {k: math.exp(v - max_v) for k, v in scores.items()}
    total = sum(exps.values())
    return {k: v / total for k, v in exps.items()}


def get_ratios(user: User) -> dict:
    scores = get_scores(user)
    raw = softmax(scores)
    min_ratio = 0.03
    adjusted = {k: max(v, min_ratio) for k, v in raw.items()}
    total = sum(adjusted.values())
    return {k: v / total for k, v in adjusted.items()}


def update_score(db: Session, user: User, category: str):
    ratios = get_ratios(user)
    current_ratio = ratios.get(category, 0)
    decay = max(0.1, 1.0 - (current_ratio / SATURATION))
    col = f"score_{category}"
    setattr(user, col, getattr(user, col) + 1.0 * decay)
    db.commit()


def get_recommendations(db: Session, user_id: int, total: int = 20) -> list:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return []

    clicked_urls = set(
        log.news_url
        for log in db.query(UserLog)
        .filter(UserLog.user_id == user_id, UserLog.action == "click")
        .all()
    )

    ratios = get_ratios(user)

    counts = {}
    assigned = 0
    sorted_cats = sorted(ratios.items(), key=lambda x: x[1], reverse=True)
    for i, (cat, ratio) in enumerate(sorted_cats):
        if i == len(sorted_cats) - 1:
            counts[cat] = max(1, total - assigned)
        else:
            n = max(1, round(total * ratio))
            counts[cat] = n
            assigned += n

    result = []
    seen_urls = set()
    for cat, count in counts.items():
        articles = fetch_rss(cat, count, clicked_urls | seen_urls)
        random.shuffle(articles)
        for article in articles[:count]:
            if article["url"] not in seen_urls:
                seen_urls.add(article["url"])
                result.append(article)

    random.shuffle(result)
    return result[:total]
