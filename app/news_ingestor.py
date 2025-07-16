import requests
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GNEWS_KEY")
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["ask_the_news"]
collection = db["articles"]

def fetch_articles(topic: str, max_articles: int = 10):
    query = topic.replace(" ", "+")
    url = f"https://gnews.io/api/v4/search?q=tesla&lang=en&apikey={API_KEY}"

    response = requests.get(url)
    if response.status_code != 200:
        print(f"GNews API error: {response}")
        return

    articles = response.json().get("articles", [])
    count = 0
    for article in articles:
        count +=1
        data = {
            "title": article.get("title"),
            "description": article.get("description"),
            "content": article.get("content"),
            "publishedAt": article.get("publishedAt"),
            "url": article.get("url"),
            "source": article.get("source", {}).get("name", "unknown")
        }

        collection.update_one(
            {"url": data["url"]},
            {"$set": data},
            upsert=True
        )
    print(f"Found {count} articles")
