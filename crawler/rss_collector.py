import re
import feedparser

RSS_FEEDS = {
    "general": [
        "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=01",
        "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=03",
        "https://www.hani.co.kr/rss/politics/",
    ],
    "technology": [
        "https://www.hani.co.kr/rss/science/",
        "https://rss.etnews.com/Section901.xml",
    ],
    "business": [
        "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=02",
    ],
    "sports": [
        "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=09",
        "https://www.hani.co.kr/rss/sports/",
        "https://rss.donga.com/sports.xml",
    ],
    "science": [
        "https://www.hani.co.kr/rss/science/",
        "https://rss.etnews.com/Section901.xml",
    ],
    "health": [
        "https://rss.donga.com/health.xml",
    ],
    "entertainment": [
        "https://news.sbs.co.kr/news/SectionRssFeed.do?sectionId=14",
        "https://rss.donga.com/entertainment.xml",
    ],
}

def strip_html(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&[a-zA-Z]+;', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def fetch_rss(category: str, count: int, exclude_urls: set) -> list:
    articles = []
    for feed_url in RSS_FEEDS.get(category, []):
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                url = getattr(entry, "link", None)
                title = getattr(entry, "title", None)
                if not url or not title:
                    continue
                if url in exclude_urls:
                    continue
                description = strip_html(getattr(entry, "summary", "") or "")
                if not description:
                    continue
                if len(description) > 200:
                    description = description[:200] + "..."
                articles.append({
                    "title":       title,
                    "description": description,
                    "url":         url,
                    "category":    category,
                })
                if len(articles) >= count * 3:
                    break
        except Exception:
            continue
        if len(articles) >= count * 3:
            break
    return articles
