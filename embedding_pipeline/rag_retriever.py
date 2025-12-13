"""
RAG Retriever Module
Provides retrieval-augmented generation interface for querying stored embeddings
"""
from embedder import CohereEmbedder
from storage import QdrantStorage
from config import COLLECTION_NAME
import logging

logger = logging.getLogger(__name__)

class RAGRetriever:
    def __init__(self, collection_name: str = COLLECTION_NAME):
        """
        Initialize the RAG retriever
        :param collection_name: Name of the collection to retrieve from
        """
        self.embedder = CohereEmbedder()
        self.storage = QdrantStorage()
        self.collection_name = collection_name

    def retrieve(self, query: str, top_k: int = 5, filter_by_url: str = None) -> List[Dict]:
        """
        Retrieve relevant documents for a query
        :param query: Query string
        :param top_k: Number of top results to return
        :param filter_by_url: Optional URL to filter results by
        :return: List of retrieved documents with relevance scores
        """
        # Generate embedding for the query
        query_embedding = self.embedder.embed_single_text(query)

        # Prepare filter conditions if needed
        filter_conditions = {}
        if filter_by_url:
            filter_conditions["source_url"] = filter_by_url

        # Search for similar documents
        results = self.storage.search_similar(
            query_embedding=query_embedding,
            collection_name=self.collection_name,
            limit=top_k,
            filter_conditions=filter_conditions
        )

        return results

    def retrieve_and_format(self, query: str, top_k: int = 5, filter_by_url: str = None) -> str:
        """
        Retrieve documents and format them as a context string for LLM consumption
        :param query: Query string
        :param top_k: Number of top results to return
        :param filter_by_url: Optional URL to filter results by
        :return: Formatted context string
        """
        results = self.retrieve(query, top_k, filter_by_url)

        # Format results as a context string
        context_parts = []
        for i, result in enumerate(results):
            context_parts.append(
                f"Document {i+1} (Score: {result['score']:.3f}, Source: {result['source_url']}):\n"
                f"{result['text']}\n"
            )

        return "\n".join(context_parts)

    def get_document_count(self) -> int:
        """
        Get the total number of documents in the collection
        :return: Total document count
        """
        info = self.storage.get_collection_info(self.collection_name)
        return info.get('vectors_count', 0)