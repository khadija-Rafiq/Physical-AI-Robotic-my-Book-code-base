"""
Embedding Pipeline for Docusaurus Documentation
Main entry point for the embedding pipeline
"""
from crawler import DocusaurusCrawler
from processor import TextProcessor
from embedder import CohereEmbedder
from storage import QdrantStorage
from config import COLLECTION_NAME
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingPipeline:
    def __init__(self):
        self.crawler = DocusaurusCrawler()
        self.processor = TextProcessor()
        self.embedder = CohereEmbedder()
        self.storage = QdrantStorage()

    def run(self, urls, collection_name=COLLECTION_NAME):
        """
        Run the complete embedding pipeline
        :param urls: List of URLs to process
        :param collection_name: Name of the Qdrant collection
        """
        logger.info(f"Starting embedding pipeline for {len(urls)} URLs")

        # Initialize storage
        self.storage.create_collection(collection_name)

        # Process each URL
        for url in urls:
            logger.info(f"Processing URL: {url}")

            # Crawl and extract text
            raw_content = self.crawler.extract_text_from_url(url)

            # Process and chunk text
            chunks = self.processor.chunk_text(raw_content, url)

            # Generate embeddings
            embeddings = self.embedder.generate_embeddings([chunk['text'] for chunk in chunks])

            # Store in Qdrant
            self.storage.store_embeddings(chunks, embeddings, collection_name)

        logger.info("Embedding pipeline completed successfully")

if __name__ == "__main__":
    # Example usage
    urls = [
        "https://docusaurus.io/docs",
        "https://docusaurus.io/docs/getting-started"
    ]

    pipeline = EmbeddingPipeline()
    pipeline.run(urls)