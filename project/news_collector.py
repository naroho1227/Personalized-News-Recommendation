
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
        "country": "kr",   
        "pageSize": 10,    
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)

    print("상태코드:", response.status_code)

    data = response.json()

    articles = data.get("articles", [])

    news_list = []

    for article in articles:
        news = {
            "title": article["title"],
            "content": article.get("content"),
            "description": article["description"],
            "author": article.get("author"),
            "source_name": article.get("source", {}).get("name"),
            "url": article.get("url"),
            "published_at": article.get("publishedAt"),
            "category": "general",
            "created_at": datetime.now()
        }
        news_list.append(news)

    return news_list

def main():
    news_list = fetch_news()

    for news in news_list:
        insert_news(news)

    print("DB 저장 완료!")

if __name__ == "__main__":
    main()
    
    conn.execute(news_table.insert(), news)
