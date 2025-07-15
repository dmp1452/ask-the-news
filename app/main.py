from fastapi import FastAPI, Query
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from app.embeddings import load_index, search_index, vector_id_map
import numpy as np
import os
from dotenv import load_dotenv
from app.llm import use_ollama
from bson import ObjectId
from app.news_ingestor import fetch_and_store_news
import app.embed_articles
load_dotenv()


embedder = SentenceTransformer("all-MiniLM-L6-v2")
index, vector_id_map = load_index()

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
    update = question.update
    if update:
        fetch_and_store_news()


    query_embedding = embedder.encode(query)
    indices, scores = search_index(index, query_embedding, top_k=5)

    matched_ids = [vector_id_map[i] for i in indices if i < len(vector_id_map)]
    articles = list(collection.find({"_id": {"$in": [ObjectId(id) for id in matched_ids]}}))
    context = "\n\n".join(f"{a['title']}\n{a['content']}" for a in articles)

    answer = use_ollama(query,context)

    return {
        "question": query,
        "answer": answer,
        "sources_used": [a['title'] for a in articles]
    }