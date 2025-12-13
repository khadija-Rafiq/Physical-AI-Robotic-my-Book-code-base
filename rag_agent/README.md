# RAG Agent Backend

A RAG (Retrieval Augmented Generation) agent built with FastAPI and OpenAI that integrates with Qdrant for question-answering based on book content.

## Features

- **Question-Answering**: Processes user queries and retrieves relevant content from stored embeddings
- **Qdrant Integration**: Uses vector similarity search to find relevant content chunks
- **OpenAI Integration**: Generates contextually accurate answers using GPT models
- **Concurrent Request Handling**: Supports multiple simultaneous requests
- **Comprehensive Logging**: Tracks the retrieval → answer flow with detailed metrics
- **FastAPI Endpoints**: RESTful API for easy integration

## Prerequisites

- Python 3.8+
- OpenAI API key
- Cohere API key (for embeddings)
- Qdrant Cloud instance or local installation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
# Or if using uv:
uv pip install -e .
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Make sure the Qdrant collection "rag_embedding" exists with the book content embeddings

## Usage

### Start the Server

```bash
cd rag_agent
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### API Endpoints

- `GET /health` - Health check
- `POST /ask` - Ask a question and get an answer
- `GET /collections` - List available Qdrant collections
- `GET /stats` - Get RAG agent statistics
- `POST /test_concurrent` - Test concurrent request handling

### Example Request

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is Physical AI?",
    "top_k": 5,
    "max_tokens": 500
  }'
```

## Architecture

The RAG agent follows this flow:

1. **Query Processing**: User question is received via FastAPI endpoint
2. **Embedding Generation**: Question is converted to embedding using Cohere
3. **Vector Search**: Qdrant performs similarity search to find relevant chunks
4. **Context Assembly**: Relevant chunks are sorted by relevance score and assembled
5. **Answer Generation**: OpenAI generates answer based on context
6. **Response**: Answer with metadata is returned to user

## Configuration

- `OPENAI_API_KEY`: Your OpenAI API key
- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_URL`: Qdrant Cloud instance URL (optional, for cloud)
- `QDRANT_API_KEY`: Qdrant API key (for cloud instances)
- `QDRANT_HOST`: Qdrant host (default: localhost, for local)
- `QDRANT_PORT`: Qdrant port (default: 6333, for local)

## Testing

Run the test suite to validate all success criteria:

```bash
python test_agent.py
```

The test suite validates:
- Agent processes user queries and retrieves relevant chunks
- Responses are contextually accurate using retrieved data
- FastAPI endpoints return answers correctly
- Pipeline handles concurrent requests without errors
- Logs show retrieval → answer flow

## Performance

- Response times typically under 2-3 seconds
- Concurrent request handling with thread-safe request counting
- Context-aware answer generation with proper citation
- Efficient chunk retrieval with relevance scoring

## Target Audience

Backend developers implementing RAG-enabled agents for AI chatbots that need to answer questions based on specific document collections.