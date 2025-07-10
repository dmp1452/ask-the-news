import requests
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("NEWS_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["ask_the_news"]
collection = db['articles']

def fetch_and_store_news():
     url = f"https://newsapi.org/v2/top-headlines?country=us&pageSize=10&apiKey={API_KEY}"
     response = requests.get(url)
     articles = response.json().get("articles",[])

     for article in articles:
          collection.update_one(
               {"url": article["url"]},
                {"$set": {
                    "title": article["title"],
                    "description": article["description"],
                    "content": article["content"],
                    "publishedAt": article["publishedAt"],
                    "source": article["source"]["name"]
                }},
                upsert = True
          )
if __name__ == "__main__":
    fetch_and_store_news()