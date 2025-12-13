"""
Retrieval Pipeline Testing
Module for testing the retrieval functionality from Qdrant
"""
import os
import sys
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import cohere

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize clients
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")  # For cloud instance
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

cohere_client = cohere.Client(COHERE_API_KEY)

# Use cloud instance if QDRANT_URL is provided, otherwise use local instance
if QDRANT_URL:
    qdrant_client = QdrantClient(
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        https=True
    )
else:
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

class QdrantRetrievalTester:
    def __init__(self, collection_name: str = "rag_embedding"):
        self.collection_name = collection_name
        self.client = qdrant_client

    def connect_to_collection(self) -> bool:
        """
        Test connection to Qdrant collection
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            logger.info(f"Successfully connected to collection '{self.collection_name}'")
            logger.info(f"Collection vectors count: {collection_info.points_count}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to collection '{self.collection_name}': {str(e)}")
            return False

    def search_similar_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar chunks based on a query
        """
        try:
            # Generate embedding for the query
            response = cohere_client.embed(
                texts=[query],
                model="embed-multilingual-v3.0",
                input_type="search_query"  # Optimize for search queries
            )
            query_embedding = response.embeddings[0]

            # Perform similarity search - using query_points method for vector search
            search_response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_k,
                with_payload=True
            )

            # Extract results from the response object
            search_results = search_response.points

            # Format results
            formatted_results = []
            for result in search_results:
                formatted_result = {
                    "id": result.id,
                    "score": result.score,
                    "text": result.payload.get("text", ""),
                    "source_url": result.payload.get("source_url", ""),
                    "start_pos": result.payload.get("start_pos"),
                    "end_pos": result.payload.get("end_pos"),
                    "chunk_id": result.payload.get("chunk_id")
                }
                formatted_results.append(formatted_result)

            logger.info(f"Found {len(formatted_results)} similar chunks for query: '{query[:50]}...'")
            return formatted_results

        except Exception as e:
            logger.error(f"Error during similarity search: {str(e)}")
            return []

    def verify_chunk_integrity(self, chunk: Dict) -> bool:
        """
        Verify that a chunk has all required metadata and content
        """
        required_fields = ["text", "source_url", "start_pos", "end_pos", "chunk_id"]
        missing_fields = [field for field in required_fields if field not in chunk or chunk[field] is None]

        if missing_fields:
            logger.warning(f"Chunk missing required fields: {missing_fields}")
            return False

        # Check if text content is substantial
        if not chunk["text"] or len(chunk["text"].strip()) < 10:
            logger.warning(f"Chunk has insufficient text content")
            return False

        # Check if source URL is valid
        if not chunk["source_url"] or not chunk["source_url"].startswith("http"):
            logger.warning(f"Chunk has invalid source URL: {chunk['source_url']}")
            return False

        logger.debug(f"Chunk integrity verified for URL: {chunk['source_url'][:50]}...")
        return True

    def validate_retrieval_accuracy(self, query: str, expected_urls: List[str] = None) -> Dict:
        """
        Validate that retrieval returns relevant results
        """
        results = self.search_similar_chunks(query, top_k=5)
        validation_report = {
            "query": query,
            "total_results": len(results),
            "valid_chunks": 0,
            "invalid_chunks": 0,
            "relevant_results": 0,
            "results": []
        }

        for result in results:
            is_valid = self.verify_chunk_integrity(result)
            if is_valid:
                validation_report["valid_chunks"] += 1
            else:
                validation_report["invalid_chunks"] += 1

            # Check if result is relevant based on expected URLs if provided
            if expected_urls and result["source_url"] in expected_urls:
                validation_report["relevant_results"] += 1

            validation_report["results"].append({
                "id": result["id"],
                "score": result["score"],
                "source_url": result["source_url"],
                "text_preview": result["text"][:100] + "..." if len(result["text"]) > 100 else result["text"],
                "is_valid": is_valid
            })

        return validation_report

    def run_comprehensive_test(self) -> Dict:
        """
        Run comprehensive tests on the retrieval pipeline
        """
        logger.info("Starting comprehensive retrieval pipeline test...")

        # Test connection
        connection_ok = self.connect_to_collection()
        if not connection_ok:
            logger.error("Cannot proceed without successful connection to Qdrant")
            return {"status": "failed", "error": "Connection failed"}

        # Define test queries and expected URLs (if known)
        test_queries = [
            "Physical AI and Robotics",
            "Humanoid Robotics Foundations",
            "What is Physical AI",
            "Introduction to the book",
            "Robotics applications"
        ]

        test_results = {
            "connection_ok": connection_ok,
            "total_queries": len(test_queries),
            "queries_results": [],
            "overall_stats": {
                "total_results": 0,
                "valid_chunks": 0,
                "invalid_chunks": 0,
                "relevant_results": 0
            }
        }

        for query in test_queries:
            logger.info(f"Testing query: '{query}'")
            query_result = self.validate_retrieval_accuracy(query)
            test_results["queries_results"].append(query_result)

            # Update overall stats
            test_results["overall_stats"]["total_results"] += query_result["total_results"]
            test_results["overall_stats"]["valid_chunks"] += query_result["valid_chunks"]
            test_results["overall_stats"]["invalid_chunks"] += query_result["invalid_chunks"]
            test_results["overall_stats"]["relevant_results"] += query_result["relevant_results"]

        logger.info("Comprehensive retrieval test completed")
        return test_results

    def test_multiple_queries(self, queries: List[str], top_k: int = 5) -> Dict:
        """
        Test the pipeline with multiple queries to ensure stability
        """
        logger.info(f"Testing multiple queries ({len(queries)} total)")

        results = {
            "queries_processed": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "errors": [],
            "average_results_per_query": 0,
            "total_results": 0
        }

        all_query_results = []

        for i, query in enumerate(queries):
            try:
                logger.debug(f"Processing query {i+1}/{len(queries)}: '{query}'")
                query_results = self.search_similar_chunks(query, top_k)

                results["queries_processed"] += 1
                results["successful_queries"] += 1
                results["total_results"] += len(query_results)

                all_query_results.append({
                    "query": query,
                    "result_count": len(query_results),
                    "results": query_results
                })

            except Exception as e:
                logger.error(f"Error processing query '{query}': {str(e)}")
                results["failed_queries"] += 1
                results["errors"].append({"query": query, "error": str(e)})

        if results["queries_processed"] > 0:
            results["average_results_per_query"] = results["total_results"] / results["queries_processed"]

        return results

def print_test_report(report: Dict):
    """
    Print a formatted test report
    """
    print("\n" + "="*60)
    print("RETRIEVAL PIPELINE TEST REPORT")
    print("="*60)

    if "connection_ok" in report:
        print(f"Connection to Qdrant: {'[PASS]' if report['connection_ok'] else '[FAIL]'}")
        print(f"Total queries tested: {report['total_queries']}")

        print("\nOverall Statistics:")
        stats = report['overall_stats']
        print(f"  Total results retrieved: {stats['total_results']}")
        print(f"  Valid chunks: {stats['valid_chunks']}")
        print(f"  Invalid chunks: {stats['invalid_chunks']}")
        print(f"  Relevant results: {stats['relevant_results']}")

        print("\nPer-Query Results:")
        for i, query_result in enumerate(report['queries_results']):
            print(f"\n  Query {i+1}: '{query_result['query']}'")
            print(f"    Results found: {query_result['total_results']}")
            print(f"    Valid chunks: {query_result['valid_chunks']}")
            print(f"    Invalid chunks: {query_result['invalid_chunks']}")

    elif "queries_processed" in report:
        print(f"Queries processed: {report['queries_processed']}")
        print(f"Successful queries: {report['successful_queries']}")
        print(f"Failed queries: {report['failed_queries']}")
        print(f"Average results per query: {report['average_results_per_query']:.2f}")
        print(f"Total results: {report['total_results']}")

    print("="*60)

if __name__ == "__main__":
    tester = QdrantRetrievalTester()

    # Run comprehensive test
    print("Running comprehensive retrieval pipeline test...")
    comprehensive_report = tester.run_comprehensive_test()
    print_test_report(comprehensive_report)

    # Test multiple queries for stability
    print("\nTesting multiple queries for stability...")
    stability_queries = [
        "Physical AI concepts",
        "Robotics technology",
        "Humanoid movement",
        "AI in robotics",
        "Machine learning applications"
    ]
    stability_report = tester.test_multiple_queries(stability_queries)
    print_test_report(stability_report)

    # Run specific validation tests
    print("\nRunning specific validation tests...")
    specific_query = "What is Physical AI?"
    specific_result = tester.validate_retrieval_accuracy(specific_query)

    print(f"\nSpecific test for query: '{specific_query}'")
    print(f"Results found: {specific_result['total_results']}")
    print(f"Valid chunks: {specific_result['valid_chunks']}")
    print(f"Invalid chunks: {specific_result['invalid_chunks']}")

    print("\nTop 3 results:")
    for i, result in enumerate(specific_result['results'][:3]):
        print(f"  {i+1}. Score: {result['score']:.3f}")
        print(f"     URL: {result['source_url']}")
        print(f"     Preview: {result['text_preview']}")
        print(f"     Valid: {'Yes' if result['is_valid'] else 'No'}")