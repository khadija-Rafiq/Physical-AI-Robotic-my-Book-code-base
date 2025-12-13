# Docusaurus RAG Backend

Backend system for fetching, processing, and storing Docusaurus documentation with Cohere embeddings in Qdrant.

## Features

- Fetches content from deployed Docusaurus sites
- Extracts and cleans text content
- Chunks text appropriately for embedding
- Generates embeddings using Cohere
- Stores embeddings in Qdrant with metadata

## Prerequisites

- Python 3.8+
- Cohere API key
- Qdrant Cloud instance or local installation

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## Usage

Run the complete pipeline:
```bash
python main.py
```

The system will:
1. Fetch all URLs from the deployed Docusaurus site
2. Extract text from each URL
3. Chunk the text into appropriate sizes
4. Generate embeddings using Cohere
5. Store embeddings in Qdrant with metadata

## Configuration

- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_URL`: Qdrant Cloud instance URL (optional, for cloud)
- `QDRANT_API_KEY`: Qdrant API key (for cloud instances)
- `QDRANT_HOST`: Qdrant host (default: localhost, for local)
- `QDRANT_PORT`: Qdrant port (default: 6333, for local)

## Functions

The main.py file contains these key functions:

- `get_all_urls()`: Fetches all URLs from the deployed site
- `extract_text_from_url()`: Extracts clean text from a URL
- `chunk_text()`: Splits text into appropriately sized chunks
- `embed()`: Generates embeddings using Cohere
- `create_collection()`: Creates the "rag_embedding" collection
- `save_chunk_to_qdrant()`: Stores embeddings with metadata in Qdrant
- `main()`: Orchestrates the complete pipeline

## Target URL

The system is configured to process: `https://physical-ai-robotic-my-book-code-ba.vercel.app/`