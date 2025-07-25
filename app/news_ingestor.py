import requests
import os
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import quote_plus
from newspaper import Article  # NEW: for scraping
from pymongo.errors import DuplicateKeyError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("GNEWS_KEY")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["ask_the_news"]
collection = db["articles"]

# Create a unique index on the 'url' field
collection.create_index("url", unique=True)

def fetch_articles(topic: str, max_articles: int = 10):
    encoded_query = quote_plus(topic)
    url = f"https://gnews.io/api/v4/search?q={encoded_query}&lang=en&apikey={API_KEY}&max={max_articles}"

    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"GNews API error: {response}")
        return

    articles = response.json().get("articles", [])
    count = 0
    for article in articles:
        count += 1
        full_content = ""
        article_url = article.get("url")
        if article_url:
            try:
                news_article = Article(article_url)
                news_article.download()
                news_article.parse()
                full_content = news_article.text
            except Exception as e:
                logger.warning(f"Failed to scrape {article_url}: {e}")
        data = {
            "title": article.get("title"),
            "description": article.get("description"),
            "content": full_content or article.get("content", ""),
            "publishedAt": article.get("publishedAt"),
            "url": article_url,
            "source": article.get("source", {}).get("name", "unknown")
        }

        try:
            collection.update_one(
                {"url": data["url"]},
                {"$set": data},
                upsert=True
            )
        except DuplicateKeyError:
            logger.info(f"Duplicate article found for URL: {data['url']}")
    logger.info(f"Found {count} articles on {encoded_query}")
