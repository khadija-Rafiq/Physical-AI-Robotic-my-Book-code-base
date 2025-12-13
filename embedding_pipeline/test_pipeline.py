"""
Test Script for Embedding Pipeline
Tests the complete pipeline with sample functionality
"""
import os
import sys
import logging

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import EmbeddingPipeline
from rag_retriever import RAGRetriever
from config import COLLECTION_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pipeline():
    """
    Test the complete embedding pipeline
    """
    logger.info("Starting pipeline test...")

    # Test data - using Docusaurus documentation URLs
    test_urls = [
        "https://docusaurus.io/docs/getting-started",
        "https://docusaurus.io/docs/configuration",
        "https://docusaurus.io/docs/markdown-features"
    ]

    # Initialize pipeline
    pipeline = EmbeddingPipeline()

    try:
        # Run the pipeline
        logger.info("Running embedding pipeline...")
        pipeline.run(test_urls, COLLECTION_NAME)

        logger.info("Pipeline completed successfully!")

        # Test retrieval
        logger.info("Testing retrieval functionality...")
        retriever = RAGRetriever(COLLECTION_NAME)

        # Sample query
        query = "How do I configure Docusaurus?"
        results = retriever.retrieve(query, top_k=3)

        logger.info(f"Found {len(results)} results for query: '{query}'")

        for i, result in enumerate(results):
            print(f"\nResult {i+1} (Score: {result['score']:.3f}):")
            print(f"Source: {result['source_url']}")
            print(f"Text preview: {result['text'][:200]}...")

        # Check document count
        count = retriever.get_document_count()
        logger.info(f"Total documents in collection: {count}")

    except Exception as e:
        logger.error(f"Error during pipeline test: {str(e)}")
        import traceback
        traceback.print_exc()

def test_individual_components():
    """
    Test individual components of the pipeline
    """
    logger.info("Testing individual components...")

    # Test crawler
    from crawler import DocusaurusCrawler
    crawler = DocusaurusCrawler(delay=0.5)  # Shorter delay for testing

    sample_url = "https://docusaurus.io/docs/getting-started"
    logger.info(f"Testing crawler on {sample_url}")
    text = crawler.extract_text_from_url(sample_url)
    logger.info(f"Extracted text length: {len(text)} characters")

    # Test processor
    from processor import TextProcessor
    processor = TextProcessor()
    chunks = processor.chunk_text(text[:1000], sample_url)  # Just first 1000 chars for test
    logger.info(f"Created {len(chunks)} chunks from text")

    # Test embedder
    from embedder import CohereEmbedder
    embedder = CohereEmbedder()
    sample_texts = [chunk['text'] for chunk in chunks[:2]]  # Just first 2 chunks
    embeddings = embedder.generate_embeddings(sample_texts)
    logger.info(f"Generated {len(embeddings)} embeddings of dimension {len(embeddings[0]) if embeddings else 0}")

    # Test storage
    from storage import QdrantStorage
    storage = QdrantStorage()
    storage.create_collection(COLLECTION_NAME + "_test")
    storage.store_embeddings(chunks[:2], embeddings, COLLECTION_NAME + "_test")
    logger.info("Successfully stored test embeddings in Qdrant")

    # Clean up test collection
    storage.delete_collection(COLLECTION_NAME + "_test")
    logger.info("Cleaned up test collection")

if __name__ == "__main__":
    logger.info("Running embedding pipeline tests...")

    # Test individual components first
    test_individual_components()

    # Then test the full pipeline if API keys are available
    if os.getenv("COHERE_API_KEY"):
        test_pipeline()
    else:
        logger.warning("COHERE_API_KEY not found in environment. Skipping full pipeline test.")
        logger.info("To run full pipeline test, set COHERE_API_KEY in your environment variables.")