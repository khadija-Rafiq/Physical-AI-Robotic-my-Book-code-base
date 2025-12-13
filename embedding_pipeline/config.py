import os
from dotenv import load_dotenv

load_dotenv()

# Configuration constants
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
VECTOR_DIMENSION = 1024  # Cohere embed-multilingual-v3.0 dimension
COLLECTION_NAME = "docusaurus_docs"
CHUNK_SIZE = 500  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks