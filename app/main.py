from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from app.embeddings import load_index, search_index, vector_id_map
import numpy as np
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Initialize the OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

embedder = SentenceTransformer("all-MiniLM-L6-v2")
index, _ = load_index()

mongo_uri = os.getenv("MONGO_URI")
client_mongo = MongoClient(mongo_uri)
db = client_mongo["ask_the_news"]
collection = db["articles"]

app = FastAPI()

class Question(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(question: Question):
    query = question.query

    query_embedding = embedder.encode(query)

    indices, scores = search_index(index, query_embedding, top_k=5)

    matched_ids = [vector_id_map[i] for i in indices if i < len(vector_id_map)]
    articles = list(collection.find({"_id": {"$in": [eval(id) for id in matched_ids]}}))

    context = "\n\n".join(f"{a['title']}\n{a['content']}" for a in articles)

    prompt = f"""You are a helpful assistant. Use the following news articles to answer the user's question.

Question: {query}

News Articles:
{context}

Answer:"""

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions using recent news."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.5
    )

    answer = response.choices[0].message.content

    return {
        "question": query,
        "answer": answer,
        "sources_used": [a['title'] for a in articles]
    }
