"""
Qdrant Retrieval Pipeline
Module for connecting to Qdrant, executing test queries, verifying metadata, and assessing relevance
"""
import os
import sys
import logging
from typing import List, Dict, Optional, Tuple
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import cohere
import time
from datetime import datetime

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

class QdrantRetrievalPipeline:
    def __init__(self, collection_name: str = "rag_embedding"):
        self.collection_name = collection_name
        self.client = qdrant_client
        self.cohere_client = cohere_client

    def connect_to_collection(self) -> bool:
        """
        Connect to Qdrant collection and verify connection
        """
        logger.info(f"Connecting to Qdrant collection: {self.collection_name}")
        try:
            collection_info = self.client.get_collection(self.collection_name)
            logger.info(f"Successfully connected to collection '{self.collection_name}'")
            logger.info(f"Collection vectors count: {collection_info.points_count}")
            logger.info(f"Collection vector size: {collection_info.config.params.vectors.size}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to collection '{self.collection_name}': {str(e)}")
            return False

    def load_sample_embeddings(self, limit: int = 10) -> List[Dict]:
        """
        Load sample embeddings from the Qdrant collection
        """
        logger.info(f"Loading {limit} sample embeddings from collection")
        try:
            # Use scroll to get sample points
            sample_results = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_payload=True,
                with_vectors=False  # Don't load vectors to save memory
            )

            samples = []
            for point in sample_results[0]:  # Results are returned as (points, next_page_offset)
                sample = {
                    "id": point.id,
                    "payload": point.payload,
                    "vector_size": len(point.vector) if point.vector else "N/A"
                }
                samples.append(sample)

            logger.info(f"Loaded {len(samples)} sample embeddings")
            return samples

        except Exception as e:
            logger.error(f"Failed to load sample embeddings: {str(e)}")
            return []

    def execute_test_query(self, query: str, top_n: int = 5) -> List[Dict]:
        """
        Execute a test query and retrieve relevant chunks
        """
        logger.info(f"Executing test query: '{query}' (top-{top_n} results)")
        try:
            # Generate embedding for the query
            response = self.cohere_client.embed(
                texts=[query],
                model="embed-multilingual-v3.0",
                input_type="search_query"  # Optimize for search queries
            )
            query_embedding = response.embeddings[0]

            # Perform similarity search using query_points for newer Qdrant client
            search_response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=top_n,
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

            logger.info(f"Retrieved {len(formatted_results)} results for query: '{query}'")
            return formatted_results

        except Exception as e:
            logger.error(f"Error executing test query '{query}': {str(e)}")
            return []

    def verify_metadata_integrity(self, chunk: Dict) -> Tuple[bool, List[str]]:
        """
        Verify metadata integrity and chunk correctness
        """
        issues = []

        # Check required fields
        required_fields = ["text", "source_url", "start_pos", "end_pos", "chunk_id"]
        for field in required_fields:
            if field not in chunk or chunk[field] is None:
                issues.append(f"Missing required field: {field}")

        # Check content quality
        if not chunk.get("text") or len(chunk["text"].strip()) < 10:
            issues.append("Text content is too short or empty")

        if not chunk.get("source_url") or not chunk["source_url"].startswith("http"):
            issues.append(f"Invalid source URL: {chunk.get('source_url')}")

        # Check positional integrity
        start_pos = chunk.get("start_pos")
        end_pos = chunk.get("end_pos")
        if start_pos is not None and end_pos is not None:
            if start_pos >= end_pos:
                issues.append(f"Positional integrity issue: start_pos ({start_pos}) >= end_pos ({end_pos})")

        # Check for duplicate chunk IDs in a broader context would require more complex checking
        is_valid = len(issues) == 0
        return is_valid, issues

    def assess_relevance(self, query: str, results: List[Dict], expected_keywords: List[str] = None) -> Dict:
        """
        Assess relevance of top-N retrievals
        """
        if not results:
            return {
                "query": query,
                "total_results": 0,
                "relevant_results": 0,
                "relevance_percentage": 0,
                "avg_score": 0,
                "keyword_matches": 0
            }

        relevant_count = 0
        total_score = 0
        keyword_match_count = 0

        for result in results:
            total_score += result["score"]

            # Check relevance based on score threshold (0.5 is a reasonable threshold)
            if result["score"] > 0.5:
                relevant_count += 1

            # Check for keyword matches if provided
            if expected_keywords:
                result_text = result["text"].lower()
                for keyword in expected_keywords:
                    if keyword.lower() in result_text:
                        keyword_match_count += 1
                        break  # Count once per result even if multiple keywords match

        avg_score = total_score / len(results) if results else 0
        relevance_percentage = (relevant_count / len(results)) * 100 if results else 0

        assessment = {
            "query": query,
            "total_results": len(results),
            "relevant_results": relevant_count,
            "relevance_percentage": relevance_percentage,
            "avg_score": avg_score,
            "keyword_matches": keyword_match_count
        }

        logger.info(f"Query '{query}' relevance: {relevance_percentage:.1f}% ({relevant_count}/{len(results)}) with avg score {avg_score:.3f}")
        return assessment

    def handle_repeated_queries(self, queries: List[str], top_n: int = 5, max_attempts: int = 3) -> Dict:
        """
        Test pipeline stability with repeated queries
        """
        logger.info(f"Testing repeated query handling with {len(queries)} queries")

        results = {
            "total_queries": len(queries),
            "successful_queries": 0,
            "failed_queries": 0,
            "attempts_made": 0,
            "errors": [],
            "avg_response_time": 0,
            "total_response_time": 0
        }

        total_time = 0
        successful_count = 0

        for query in queries:
            attempt = 0
            success = False

            while attempt < max_attempts and not success:
                results["attempts_made"] += 1
                attempt += 1

                start_time = time.time()
                try:
                    query_results = self.execute_test_query(query, top_n)
                    response_time = time.time() - start_time
                    total_time += response_time
                    successful_count += 1

                    # Verify results integrity
                    valid_results = 0
                    for result in query_results:
                        is_valid, _ = self.verify_metadata_integrity(result)
                        if is_valid:
                            valid_results += 1

                    logger.debug(f"Query '{query}' completed successfully with {valid_results}/{len(query_results)} valid results")
                    success = True
                    results["successful_queries"] += 1

                except Exception as e:
                    error_msg = f"Query '{query}' attempt {attempt} failed: {str(e)}"
                    logger.warning(error_msg)

                    if attempt >= max_attempts:
                        results["failed_queries"] += 1
                        results["errors"].append(error_msg)

                    # Add small delay before retry
                    time.sleep(0.5)

        results["total_response_time"] = total_time
        results["avg_response_time"] = total_time / successful_count if successful_count > 0 else 0

        logger.info(f"Repeated query test completed: {results['successful_queries']}/{results['total_queries']} successful, avg response time: {results['avg_response_time']:.3f}s")
        return results

    def log_query_results(self, query: str, results: List[Dict], assessment: Dict):
        """
        Log detailed results for a query
        """
        logger.info(f"--- Query Results for: '{query}' ---")
        logger.info(f"Total results: {len(results)}")
        logger.info(f"Relevance: {assessment['relevance_percentage']:.1f}%")
        logger.info(f"Average score: {assessment['avg_score']:.3f}")

        for i, result in enumerate(results[:3], 1):  # Log top 3 results
            logger.info(f"  Result {i}: Score={result['score']:.3f}, URL={result['source_url'][:50]}...")
            logger.info(f"    Text preview: {result['text'][:100]}...")

        logger.info("--- End Query Results ---")

    def run_complete_pipeline(self) -> Dict:
        """
        Run the complete pipeline: connect, load samples, execute queries, verify, assess, repeat
        """
        logger.info("Starting complete Qdrant retrieval pipeline...")

        start_time = time.time()

        # Step 1: Connect to collection
        connection_ok = self.connect_to_collection()
        if not connection_ok:
            logger.error("Cannot proceed without successful connection to Qdrant")
            return {"status": "failed", "error": "Connection failed"}

        # Step 2: Load sample embeddings
        samples = self.load_sample_embeddings(limit=5)
        logger.info(f"Sample embeddings loaded: {len(samples)}")

        # Step 3: Execute test queries
        test_queries = [
            "Physical AI and Robotics",
            "Humanoid Robotics Foundations",
            "What is Physical AI?",
            "Introduction to the book",
            "Robotics applications"
        ]

        query_results = []
        assessments = []

        for query in test_queries:
            results = self.execute_test_query(query, top_n=5)
            assessment = self.assess_relevance(
                query,
                results,
                expected_keywords=query.split()  # Use query words as expected keywords
            )

            # Verify metadata integrity for each result
            integrity_issues = 0
            for result in results:
                is_valid, issues = self.verify_metadata_integrity(result)
                if not is_valid:
                    integrity_issues += 1
                    logger.debug(f"Metadata issues in result from {result['source_url']}: {issues}")

            assessment["integrity_issues"] = integrity_issues
            query_results.append(results)
            assessments.append(assessment)

            # Log results
            self.log_query_results(query, results, assessment)

        # Step 4: Handle repeated queries to test stability
        repeated_query_results = self.handle_repeated_queries(
            queries=["Physical AI", "Robotics", "Humanoid"],
            top_n=3,
            max_attempts=2
        )

        # Step 5: Generate final assessment
        total_results = sum(len(results) for results in query_results)
        total_relevant = sum(ass["relevant_results"] for ass in assessments)
        avg_relevance = sum(ass["relevance_percentage"] for ass in assessments) / len(assessments) if assessments else 0
        avg_score = sum(ass["avg_score"] for ass in assessments) / len(assessments) if assessments else 0

        final_report = {
            "status": "completed",
            "connection_ok": connection_ok,
            "samples_loaded": len(samples),
            "queries_executed": len(test_queries),
            "total_results_retrieved": total_results,
            "total_relevant_results": total_relevant,
            "average_relevance_percentage": avg_relevance,
            "average_score": avg_score,
            "repeated_query_results": repeated_query_results,
            "individual_assessments": assessments,
            "pipeline_duration": time.time() - start_time
        }

        logger.info("=== FINAL PIPELINE ASSESSMENT ===")
        logger.info(f"Pipeline Duration: {final_report['pipeline_duration']:.2f}s")
        logger.info(f"Connection Status: {'✓' if final_report['connection_ok'] else '✗'}")
        logger.info(f"Samples Loaded: {final_report['samples_loaded']}")
        logger.info(f"Queries Executed: {final_report['queries_executed']}")
        logger.info(f"Total Results: {final_report['total_results_retrieved']}")
        logger.info(f"Relevant Results: {final_report['total_relevant_results']}")
        logger.info(f"Average Relevance: {final_report['average_relevance_percentage']:.2f}%")
        logger.info(f"Average Score: {final_report['average_score']:.3f}")
        logger.info(f"Repeated Query Success Rate: {repeated_query_results['successful_queries']}/{repeated_query_results['total_queries']}")
        logger.info("===============================")

        return final_report

def main():
    """
    Main function to execute the complete pipeline
    """
    logger.info("Initializing Qdrant Retrieval Pipeline")

    pipeline = QdrantRetrievalPipeline()
    report = pipeline.run_complete_pipeline()

    if report["status"] == "completed":
        logger.info("Pipeline completed successfully!")
        return 0
    else:
        logger.error("Pipeline failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())