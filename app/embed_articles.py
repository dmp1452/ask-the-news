from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np
from app.embeddings import create_index, add_to_index, save_index
import os
from dotenv import load_dotenv


load_dotenv()

mongo_uri = os.getenv("MONGO_URI") 

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["ask_the_news"]
collection = db["articles"]
model = SentenceTransformer("all-MiniLM-L6-v2")

index= create_index()
def embed_articles():
    print("Embedding and indexing articles")
    count = 0
    for article in collection.find():
        text = f"{article.get('title'),''}{article.get('content','')}".strip()
        if not text:
            continue
        embedding = model.encode(text)
        add_to_index(index, embedding, article_id=str(article["_id"]))
        count +=1

    print(f"✅ Embedded and indexed {count} articles.")
    save_index(index)
    print("index and id map saved")