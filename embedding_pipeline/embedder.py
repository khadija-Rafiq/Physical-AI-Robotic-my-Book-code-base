"""
Cohere Embedder Module
Handles generating embeddings using the Cohere API
"""
import cohere
from typing import List, Dict
import time
import logging
from config import COHERE_API_KEY

logger = logging.getLogger(__name__)

class CohereEmbedder:
    def __init__(self, model: str = "embed-multilingual-v3.0"):
        """
        Initialize the Cohere embedder
        :param model: Cohere embedding model to use
        """
        if not COHERE_API_KEY:
            raise ValueError("COHERE_API_KEY environment variable must be set")

        self.client = cohere.Client(COHERE_API_KEY)
        self.model = model

    def generate_embeddings(self, texts: List[str], batch_size: int = 96) -> List[List[float]]:
        """
        Generate embeddings for a list of texts
        :param texts: List of texts to embed
        :param batch_size: Number of texts to process in each batch
        :return: List of embeddings (each embedding is a list of floats)
        """
        all_embeddings = []

        # Process in batches to respect API limits
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                response = self.client.embed(
                    texts=batch,
                    model=self.model,
                    input_type="search_document"  # Optimize for document search
                )

                batch_embeddings = response.embeddings
                all_embeddings.extend(batch_embeddings)

                logger.info(f"Generated embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")

                # Add a small delay to be respectful to the API
                time.sleep(0.1)

            except Exception as e:
                logger.error(f"Error generating embeddings for batch {i//batch_size + 1}: {str(e)}")
                # Add placeholder embeddings for failed batch to maintain alignment
                for _ in batch:
                    all_embeddings.append([0.0] * 1024)  # Placeholder for Cohere's multilingual model

        return all_embeddings

    def embed_single_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        :param text: Text to embed
        :return: Embedding as a list of floats
        """
        try:
            response = self.client.embed(
                texts=[text],
                model=self.model,
                input_type="search_query"  # Optimize for search queries
            )

            return response.embeddings[0]
        except Exception as e:
            logger.error(f"Error generating embedding for text: {str(e)}")
            return [0.0] * 1024  # Return zero vector as fallback