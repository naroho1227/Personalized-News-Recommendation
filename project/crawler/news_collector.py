from db import insert_news
from datetime import datetime
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")

def fetch_news():
    url = "https://newsapi.org/v2/top-headlines"

    params = {
        "country": "us",   
        "pageSize": 10,    
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)

    print("상태코드:", response.status_code)

    data = response.json()

    articles = data.get("articles", [])

    news_list = []

    for article in articles:

        pub_at = article.get("publishedAt")
        if pub_at:
            published_at_dt = datetime.fromisoformat(pub_at.replace("Z", "+00:00"))
        else:
            published_at_dt = None

        news = {
            "title": article["title"],
            "content": article.get("content"),
            "description": article["description"],
            "author": article.get("author"),
            "source_name": article.get("source", {}).get("name"),
            "url": article.get("url"),
            "published_at": published_at_dt,
            "category": "general",
            "created_at": datetime.now()
        }
        news_list.append(news)

    return news_list

def main():
    news_list = fetch_news()
    print(f"📡 API에서 가져온 뉴스 개수: {len(news_list)}개")

    for news in news_list:
        insert_news(news)

    print("DB 저장 완료!")


if __name__ == "__main__":
    main()
