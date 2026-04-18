import requests
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database import SessionLocal, engine, Base
from backend.app.models import News

API_KEY = "3346403e22304263b5536f87c25f4baa"
URL = "https://newsapi.org/v2/top-headlines"
CATEGORIES = ["general", "technology", "business", "sports", "science", "health", "entertainment"]


def fetch_and_save_news():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    total_saved = 0

    for category in CATEGORIES:
        params = {
            "country": "us",
            "category": category,
            "pageSize": 10,
            "apiKey": API_KEY,
        }
        try:
            response = requests.get(URL, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json().get("articles", [])

            for a in articles:
                title = a.get("title")
                if not title or "[Removed]" in title:
                    continue

                if db.query(News).filter(News.title == title).first():
                    continue

                news_item = News(
                    title=title,
                    content=a.get("content") or a.get("description") or "No Content",
                    category=category,
                    description=a.get("description"),
                    url=a.get("url"),
                )
                db.add(news_item)
                total_saved += 1

        except Exception as e:
            print(f"[ERROR] {category}: {e}")
            continue

    db.commit()
    db.close()
    print(f"완료: {total_saved}건 저장됨")


if __name__ == "__main__":
    fetch_and_save_news()
