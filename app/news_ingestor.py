import feedparser
from newspaper import Article
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["ask_the_news"]
collection = db["articles"]

def fetch_articles(topic: str, max_articles: int = 10):
    """
    Fetches and stores articles related to the topic using Google News RSS.
    """
    rss_url = f"https://news.google.com/rss/search?q={topic.replace(' ', '+')}"
    feed = feedparser.parse(rss_url)
    count = 0

    for entry in feed.entries:
        if count >= max_articles:
            break

        if "url=" in entry.link:
            url = entry.link.split("url=")[-1]
        else:
            url = entry.link 

        article = Article(url)

        try:
            article.download()
            article.parse()
        except:
            continue 

        data = {
            "title": article.title,
            "content": article.text,
            "publishedAt": entry.get("published", ""),
            "url": url,
            "source": entry.get("source", {}).get("title", "unknown")
        }
        print(article.text)
        collection.update_one(
            {"url": url}, 
            {"$set": data},
            upsert=True
        )

        count += 1

    print(f"✅ Fetched and stored {count} articles for topic: '{topic}'")
