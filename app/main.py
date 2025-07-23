from fastapi import FastAPI, Query
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from app.embeddings import VectorStore
import numpy as np
import os
from dotenv import load_dotenv
from app.llm import use_ollama
from bson import ObjectId
from app.news_ingestor import fetch_articles
from app.embed_articles import embed_articles
from bson.errors import InvalidId
load_dotenv()


embedder = SentenceTransformer("all-MiniLM-L6-v2")
vector_store = VectorStore()

mongo_uri = os.getenv("MONGO_URI")
client_mongo = MongoClient(mongo_uri)
db = client_mongo["ask_the_news"]
collection = db["articles"]

app = FastAPI()

class Question(BaseModel):
    query: str
    update: bool

@app.post("/ask")
async def ask_question(question: Question):
    query = question.query
    if question.update:
        fetch_articles(query)
        embed_articles(vector_store)

    query_embedding = embedder.encode(query)
    query_embedding = query_embedding.cpu().numpy() if hasattr(query_embedding, "cpu") else query_embedding
    query_embedding = np.asarray(query_embedding)
    indices, __ = vector_store.search_index(query_embedding, top_k=3)

    current_id_map = vector_store.get_id_map()
    matched_ids = [current_id_map[i] for i in indices if i < len(current_id_map)]

   
    articles = list(collection.find({"_id": {"$in": [ObjectId(id) for id in matched_ids]}}))
    print(len(articles))
    if not articles:
        return {
            "question": query,
            "answer": "No relevant articles found to answer your question.",
            "sources_used": []
        }
    context = ""
    for article in articles:
        content = article.get('content', '').strip()
        context += f"content: {content}"
    print(context)
    answer = use_ollama(query,context)

    return {
        "question": query,
        "answer": answer,
    }