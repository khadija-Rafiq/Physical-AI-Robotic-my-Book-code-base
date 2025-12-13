# Docusaurus Embedding Pipeline

A complete pipeline for extracting text from Docusaurus documentation sites, generating embeddings using Cohere, and storing them in Qdrant for RAG-based retrieval.

## Features

- **Docusaurus-Specific Crawling**: Efficiently extracts content from Docusaurus documentation sites
- **Text Processing**: Cleans and chunks text appropriately for embedding
- **Cohere Integration**: Generates high-quality embeddings using Cohere's multilingual model
- **Qdrant Storage**: Stores embeddings in a vector database for fast similarity search
- **RAG Interface**: Provides retrieval functionality for downstream applications

## Prerequisites

- Python 3.8+
- Qdrant vector database (can run locally or remotely)
- Cohere API key

## Installation

1. Clone the repository and navigate to the embedding_pipeline directory:
```bash
cd embedding_pipeline
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your Cohere API key
```

4. Start Qdrant (if running locally):
```bash
# Option 1: Using Docker
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage:z \
    qdrant/qdrant

# Option 2: Using the hosted version
# Update QDRANT_HOST in your .env file
```

## Configuration

The pipeline can be configured via environment variables in the `.env` file:

- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_HOST`: Qdrant host (default: localhost)
- `QDRANT_PORT`: Qdrant port (default: 6333)
- `CHUNK_SIZE`: Size of text chunks in characters (default: 500)
- `CHUNK_OVERLAP`: Overlap between chunks in characters (default: 50)

## Usage

### Basic Usage

```python
from main import EmbeddingPipeline

# Initialize the pipeline
pipeline = EmbeddingPipeline()

# URLs to process
urls = [
    "https://yoursite.com/docs/intro",
    "https://yoursite.com/docs/setup",
    "https://yoursite.com/docs/api"
]

# Run the pipeline
pipeline.run(urls)
```

### Advanced Usage with Custom Collection

```python
from main import EmbeddingPipeline

pipeline = EmbeddingPipeline()
pipeline.run(urls, collection_name="my_custom_docs")
```

### Retrieval

```python
from rag_retriever import RAGRetriever

retriever = RAGRetriever(collection_name="my_custom_docs")

# Retrieve relevant documents
results = retriever.retrieve("How do I configure the API?", top_k=5)

# Or get formatted context for LLM consumption
context = retriever.retrieve_and_format("How do I deploy?", top_k=3)
```

### Testing Individual Components

Run the test script to verify all components work correctly:

```bash
python test_pipeline.py
```

## Architecture

The pipeline consists of several modular components:

1. **Crawler (`crawler.py`)**: Extracts text content from Docusaurus sites
2. **Processor (`processor.py`)**: Cleans and chunks text appropriately
3. **Embedder (`embedder.py`)**: Generates embeddings using Cohere API
4. **Storage (`storage.py`)**: Manages Qdrant vector storage
5. **RAG Retriever (`rag_retriever.py`)**: Provides retrieval interface

## Error Handling

- Network errors during crawling are logged and skipped
- Embedding API errors result in placeholder vectors to maintain alignment
- Qdrant connection errors are caught and logged
- Invalid input is sanitized before processing

## Performance Considerations

- Text is processed in chunks to respect API limits
- Batching is used for embedding generation
- Appropriate delays are added between requests to be respectful to servers
- Vector indexes are created for efficient retrieval

## Security

- API keys are loaded from environment variables
- Input text is sanitized before processing
- Connection to Qdrant is configurable for secure deployments

## License

MIT