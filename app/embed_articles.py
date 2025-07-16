from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np
from app.embeddings import VectorStore
import os
from dotenv import load_dotenv


load_dotenv()

mongo_uri = os.getenv("MONGO_URI") 

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["ask_the_news"]
collection = db["articles"]
model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_articles(vector_store: VectorStore):
    print("Embedding and indexing articles")
    count = 0
    for article in collection.find():
        text = f"{article.get('title', '')} {article.get('content', '')}".strip()
        if not text:
            continue
        try:
            embedding = model.encode(text)
            embedding = embedding.cpu().numpy() if hasattr(embedding, "cpu") else embedding
            embedding = np.asarray(embedding)
            vector_store.add_to_index(embedding, article_id=str(article["_id"]))
            count +=1
        except Exception as e:
            print(f"Error embedding article {article.get('_id')}: {e}")
            continue


    print(f"Embedded and indexed {count} articles.")
    vector_store.save_index()