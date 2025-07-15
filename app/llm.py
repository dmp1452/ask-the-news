import requests

def get_prompt(query, context):
    return ("You are an expert news analyst. Use the following news articles to answer the query below."
    "Only use information from the context provided. If the answer cannot be found in any of the articles, say \"The information is not available.\""
    f"query: {query}"
    f"context: {context}"
    "Please provide a clear, concise, and factual answer based only on the articles above.")

def use_ollama(query,context):
    url = "http://localhost:11434/api/generate"
    data = { "model": "gemma3:4b", "prompt": get_prompt(query,context), "stream": False}
    response = requests.post(url,json=data)
    response.raise_for_status()

    return response.json()["response"]