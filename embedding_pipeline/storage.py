"""
Qdrant Storage Module
Handles storing embeddings in Qdrant vector database
"""
from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict
import logging
from config import QDRANT_HOST, QDRANT_PORT, VECTOR_DIMENSION, COLLECTION_NAME

logger = logging.getLogger(__name__)

class QdrantStorage:
    def __init__(self):
        """
        Initialize the Qdrant client
        """
        # Use URL-based initialization to match backend approach for consistency
        import os
        qdrant_url = os.getenv("QDRANT_URL")
        qdrant_api_key = os.getenv("QDRANT_API_KEY")

        if qdrant_url:
            self.client = QdrantClient(
                url=qdrant_url,
                api_key=qdrant_api_key
            )
        else:
            # Fallback to host/port if URL is not provided
            self.client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    def create_collection(self, collection_name: str = COLLECTION_NAME):
        """
        Create a collection in Qdrant if it doesn't exist
        :param collection_name: Name of the collection to create
        """
        try:
            # Check if collection exists
            self.client.get_collection(collection_name)
            logger.info(f"Collection '{collection_name}' already exists")
        except:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=VECTOR_DIMENSION,  # Cohere multilingual model dimension
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection '{collection_name}' with {VECTOR_DIMENSION}-dimensional vectors")

            # Create payload index for efficient filtering by source URL
            self.client.create_payload_index(
                collection_name=collection_name,
                field_name="source_url",
                field_schema=models.PayloadSchemaType.KEYWORD
            )
            logger.info("Created payload index for source_url")

    def store_embeddings(self, chunks: List[Dict], embeddings: List[List[float]], collection_name: str = COLLECTION_NAME):
        """
        Store text chunks and their embeddings in Qdrant
        :param chunks: List of text chunks with metadata
        :param embeddings: List of corresponding embeddings
        :param collection_name: Name of the collection to store in
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")

        # Prepare points for insertion
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point = models.PointStruct(
                id=i,  # Using sequential IDs, in production you might want UUIDs
                vector=embedding,
                payload={
                    "text": chunk['text'],
                    "source_url": chunk['source_url'],
                    "start_pos": chunk['start_pos'],
                    "end_pos": chunk['end_pos'],
                    "chunk_id": chunk['chunk_id']
                }
            )
            points.append(point)

        # Upload points to Qdrant
        self.client.upsert(
            collection_name=collection_name,
            points=points
        )

        logger.info(f"Stored {len(points)} embeddings in collection '{collection_name}'")

    def search_similar(self, query_embedding: List[float], collection_name: str = COLLECTION_NAME,
                      limit: int = 5, filter_conditions: Dict = None) -> List[Dict]:
        """
        Search for similar embeddings in the collection
        :param query_embedding: Query embedding to search for
        :param collection_name: Name of the collection to search in
        :param limit: Number of results to return
        :param filter_conditions: Optional filter conditions (e.g., {"source_url": "specific_url"})
        :return: List of similar documents with scores
        """
        # Prepare filter if provided
        search_filter = None
        if filter_conditions:
            filter_conditions_list = []
            for key, value in filter_conditions.items():
                filter_conditions_list.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    )
                )

            search_filter = models.Filter(must=filter_conditions_list)

        # Check if client has search method
        if not hasattr(self.client, 'search'):
            raise Exception("Qdrant client does not have 'search' method - version incompatibility")

        # Perform search - using the correct API for Qdrant client 1.8.0
        results = self.client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=limit
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_result = {
                "id": result.id,
                "score": result.score,
                "text": result.payload.get("text", ""),
                "source_url": result.payload.get("source_url", ""),
                "metadata": {
                    "start_pos": result.payload.get("start_pos"),
                    "end_pos": result.payload.get("end_pos"),
                    "chunk_id": result.payload.get("chunk_id")
                }
            }
            formatted_results.append(formatted_result)

        return formatted_results

    def delete_collection(self, collection_name: str):
        """
        Delete a collection from Qdrant
        :param collection_name: Name of the collection to delete
        """
        try:
            self.client.delete_collection(collection_name)
            logger.info(f"Deleted collection '{collection_name}'")
        except Exception as e:
            logger.error(f"Error deleting collection '{collection_name}': {str(e)}")

    def get_collection_info(self, collection_name: str = COLLECTION_NAME) -> Dict:
        """
        Get information about a collection
        :param collection_name: Name of the collection
        :return: Collection information
        """
        try:
            collection_info = self.client.get_collection(collection_name)
            return {
                "name": collection_info.config.params.vectors.size,
                "vectors_count": collection_info.vectors_count,
                "indexed_vectors_count": collection_info.indexed_vectors_count
            }
        except Exception as e:
            logger.error(f"Error getting collection info for '{collection_name}': {str(e)}")
            return {}