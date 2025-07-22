# 📰 Ask the News

Ask the News is a backend-only FastAPI project that uses AI and semantic search to answer natural-language questions about current events.

### 🔧 Features
- FastAPI backend with `/ask` endpoint
- News ingestion via NewsAPI
- Article storage using MongoDB
- RAG (Retrieval-Augmented Generation) architecture coming soon
- Ready for vector search and LLM integration (LangChain / Hugging Face)
- Docker support for easy deployment

### 🛠 Tech Stack
- Python
- FastAPI
- MongoDB
- NewsAPI
- Uvicorn
- Docker

### 🚀 Getting Started

#### 1. Clone the repo
```bash
git clone https://github.com/your-username/ask-the-news.git
cd ask-the-news
```

#### 2. Set up environment variables
Create a `.env` file in the project root with your configuration:
```
MONGO_URI=your_mongodb_connection_string
```

#### 3. Run with Docker
```bash
docker build -t ask-the-news .
docker run -p 8000:8000 --env-file .env ask-the-news
```

#### 4. Example usage
You can use the provided `ask.py` script to test the API:
```bash
python ask.py
```
