import requests

def get_prompt(query, context):
    return ("You are an AI assistant specialized in summarizing news articles. "
        "Your task is to answer the user's question ONLY based on the provided context. "
        "If the answer cannot be found in the context, state that you don't have enough information. "
        "Do not use external knowledge. Be concise and directly answer the question."
        f"query: {query}"
        f"context: {context}"
        "Please provide a clear, concise, and factual answer based only on the articles above.")

def use_ollama(query,context):
    url = "http://localhost:11434/api/generate"
    data = { "model": "gemma3:4b", "prompt": get_prompt(query,context), "stream": False}
    response = requests.post(url,json=data)
    response.raise_for_status()

    return response.json()["response"]