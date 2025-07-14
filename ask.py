import requests

response = requests.post("http://localhost:8000/ask", json={
    "query": "What is the latest on climate change?"
})

print(response.json())
