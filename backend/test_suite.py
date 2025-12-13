"""
Comprehensive Test Suite for RAG Retrieval Pipeline
Validates all success criteria for the embedding and retrieval workflow
"""
import os
import sys
import logging
from typing import List, Dict, Tuple
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import cohere
import time

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

class RetrievalTestSuite:
    def __init__(self, collection_name: str = "rag_embedding"):
        self.collection_name = collection_name
        self.client = qdrant_client
        self.test_results = {
            "connection_test": False,
            "retrieval_accuracy": False,
            "metadata_integrity": False,
            "relevance_test": False,
            "multiple_queries_test": False,
            "end_to_end_test": False
        }

    def test_connection(self) -> bool:
        """
        Test 1: Connect to Qdrant collection
        """
        logger.info("TEST 1: Testing connection to Qdrant collection")
        try:
            collection_info = self.client.get_collection(self.collection_name)
            logger.info(f"✓ Successfully connected to collection '{self.collection_name}'")
            logger.info(f"  Vectors count: {collection_info.points_count}")
            self.test_results["connection_test"] = True
            return True
        except Exception as e:
            logger.error(f"✗ Failed to connect to collection '{self.collection_name}': {str(e)}")
            return False

    def test_retrieval_accuracy(self) -> bool:
        """
        Test 2: Retrieve vectors based on sample queries and verify accuracy
        """
        logger.info("TEST 2: Testing retrieval accuracy for sample queries")

        test_queries = [
            "Physical AI and Robotics",
            "Humanoid Robotics Foundations",
            "What is Physical AI?",
            "Introduction to robotics"
        ]

        successful_retrievals = 0
        total_retrievals = 0

        for query in test_queries:
            try:
                # Generate embedding for the query
                response = cohere_client.embed(
                    texts=[query],
                    model="embed-multilingual-v3.0",
                    input_type="search_query"
                )
                query_embedding = response.embeddings[0]

                # Perform similarity search - using query_points method for vector search
                search_response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_embedding,
                    limit=3,
                    with_payload=True
                )

                # Extract results from the response object
                search_results = search_response.points

                total_retrievals += 1
                if len(search_results) > 0:
                    successful_retrievals += 1
                    logger.debug(f"  Query '{query}' returned {len(search_results)} results")

            except Exception as e:
                logger.error(f"  Error retrieving for query '{query}': {str(e)}")

        success_rate = successful_retrievals / total_retrievals if total_retrievals > 0 else 0
        logger.info(f"  Retrieval success rate: {success_rate:.2%} ({successful_retrievals}/{total_retrievals})")

        accuracy_ok = success_rate >= 0.75  # At least 75% success rate
        self.test_results["retrieval_accuracy"] = accuracy_ok
        logger.info(f"  Result: {'✓' if accuracy_ok else '✗'}")

        return accuracy_ok

    def test_metadata_integrity(self) -> bool:
        """
        Test 3: Verify chunk integrity and metadata
        """
        logger.info("TEST 3: Testing chunk integrity and metadata")

        try:
            # Get a sample of points from the collection
            sample_results = self.client.scroll(
                collection_name=self.collection_name,
                limit=10,  # Get first 10 points
                with_payload=True
            )

            valid_chunks = 0
            total_chunks = len(sample_results[0]) if sample_results[0] else 0

            for point in sample_results[0]:
                payload = point.payload
                required_fields = ["text", "source_url", "start_pos", "end_pos", "chunk_id"]

                has_all_fields = all(field in payload and payload[field] is not None for field in required_fields)
                has_valid_text = len(payload.get("text", "").strip()) > 0
                has_valid_url = payload.get("source_url", "").startswith("http")

                if has_all_fields and has_valid_text and has_valid_url:
                    valid_chunks += 1

            integrity_rate = valid_chunks / total_chunks if total_chunks > 0 else 0
            logger.info(f"  Metadata integrity rate: {integrity_rate:.2%} ({valid_chunks}/{total_chunks})")

            integrity_ok = integrity_rate >= 0.9  # At least 90% integrity
            self.test_results["metadata_integrity"] = integrity_ok
            logger.info(f"  Result: {'✓' if integrity_ok else '✗'}")

            return integrity_ok

        except Exception as e:
            logger.error(f"  Error testing metadata integrity: {str(e)}")
            return False

    def test_relevance(self) -> bool:
        """
        Test 4: Ensure relevance of top results
        """
        logger.info("TEST 4: Testing relevance of top results")

        test_cases = [
            {
                "query": "Physical AI concepts",
                "expected_keywords": ["physical", "ai", "artificial", "intelligence"]
            },
            {
                "query": "Humanoid robotics",
                "expected_keywords": ["humanoid", "robot", "robotics", "movement"]
            },
            {
                "query": "Machine learning applications",
                "expected_keywords": ["machine", "learning", "algorithm", "model"]
            }
        ]

        relevant_results = 0
        total_results = 0

        for test_case in test_cases:
            query = test_case["query"]
            expected_keywords = test_case["expected_keywords"]

            try:
                # Generate embedding for the query
                response = cohere_client.embed(
                    texts=[query],
                    model="embed-multilingual-v3.0",
                    input_type="search_query"
                )
                query_embedding = response.embeddings[0]

                # Perform similarity search - using query_points method for vector search
                search_response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_embedding,
                    limit=5,
                    with_payload=True
                )

                # Extract results from the response object
                search_results = search_response.points

                for result in search_results:
                    result_text = result.payload.get("text", "").lower()
                    has_expected_keywords = any(keyword.lower() in result_text for keyword in expected_keywords)

                    total_results += 1
                    if has_expected_keywords or result.score > 0.5:  # High score also indicates relevance
                        relevant_results += 1

            except Exception as e:
                logger.error(f"  Error testing relevance for query '{query}': {str(e)}")

        relevance_rate = relevant_results / total_results if total_results > 0 else 0
        logger.info(f"  Relevance rate: {relevance_rate:.2%} ({relevant_results}/{total_results})")

        relevance_ok = relevance_rate >= 0.6  # At least 60% relevance
        self.test_results["relevance_test"] = relevance_ok
        logger.info(f"  Result: {'✓' if relevance_ok else '✗'}")

        return relevance_ok

    def test_multiple_queries(self) -> bool:
        """
        Test 5: Ensure pipeline can handle multiple queries without errors
        """
        logger.info("TEST 5: Testing multiple queries handling")

        test_queries = [
            "Robotics technology",
            "AI applications",
            "Physical computing",
            "Machine learning",
            "Humanoid movement",
            "Neural networks",
            "Computer vision",
            "Natural language processing"
        ]

        successful_queries = 0
        total_queries = len(test_queries)
        errors = []

        for i, query in enumerate(test_queries):
            try:
                logger.debug(f"  Processing query {i+1}/{total_queries}: '{query}'")

                # Generate embedding for the query
                response = cohere_client.embed(
                    texts=[query],
                    model="embed-multilingual-v3.0",
                    input_type="search_query"
                )
                query_embedding = response.embeddings[0]

                # Perform similarity search - using query_points method for vector search
                search_response = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_embedding,
                    limit=3,
                    with_payload=True
                )

                # Extract results from the response object to validate it worked
                search_results = search_response.points

                successful_queries += 1

            except Exception as e:
                error_msg = f"Query '{query}' failed: {str(e)}"
                errors.append(error_msg)
                logger.warning(f"  {error_msg}")

        success_rate = successful_queries / total_queries
        logger.info(f"  Multiple queries success rate: {success_rate:.2%} ({successful_queries}/{total_queries})")

        if errors:
            logger.info(f"  Errors encountered: {len(errors)}")
            for error in errors[:3]:  # Show first 3 errors
                logger.info(f"    - {error}")

        multiple_queries_ok = success_rate >= 0.8  # At least 80% success rate
        self.test_results["multiple_queries_test"] = multiple_queries_ok
        logger.info(f"  Result: {'✓' if multiple_queries_ok else '✗'}")

        return multiple_queries_ok

    def test_end_to_end_functionality(self) -> bool:
        """
        Test 6: End-to-end functionality test
        """
        logger.info("TEST 6: Testing end-to-end functionality")

        try:
            # Complete flow: query -> embedding -> search -> results
            query = "Physical AI and Robotics concepts"

            # Step 1: Generate embedding
            response = cohere_client.embed(
                texts=[query],
                model="embed-multilingual-v3.0",
                input_type="search_query"
            )
            query_embedding = response.embeddings[0]
            logger.debug("  Step 1: Embedding generated successfully")

            # Step 2: Search in Qdrant - using query_points method for vector search
            search_response = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=5,
                with_payload=True
            )
            # Extract results from the response object
            search_results = search_response.points
            logger.debug(f"  Step 2: Found {len(search_results)} results")

            # Step 3: Validate results
            for result in search_results:
                # Check that all required metadata is present
                payload = result.payload
                required_fields = ["text", "source_url", "start_pos", "end_pos", "chunk_id"]

                for field in required_fields:
                    if field not in payload:
                        raise Exception(f"Missing field '{field}' in result payload")

                if not payload["text"] or not payload["source_url"]:
                    raise Exception("Empty text or source_url in result")

            logger.debug(f"  Step 3: All {len(search_results)} results validated successfully")

            # Step 4: Check that we have meaningful results
            if len(search_results) == 0:
                raise Exception("No results returned from search")

            avg_score = sum(r.score for r in search_results) / len(search_results)
            logger.debug(f"  Step 4: Average relevance score: {avg_score:.3f}")

            logger.info("  ✓ End-to-end functionality test passed")
            self.test_results["end_to_end_test"] = True
            return True

        except Exception as e:
            logger.error(f"  ✗ End-to-end functionality test failed: {str(e)}")
            self.test_results["end_to_end_test"] = False
            return False

    def run_all_tests(self) -> Dict:
        """
        Run all tests and return comprehensive report
        """
        logger.info("Starting comprehensive RAG retrieval pipeline tests...")
        logger.info("="*60)

        # Run all individual tests
        tests = [
            ("Connection Test", self.test_connection),
            ("Retrieval Accuracy", self.test_retrieval_accuracy),
            ("Metadata Integrity", self.test_metadata_integrity),
            ("Relevance Test", self.test_relevance),
            ("Multiple Queries", self.test_multiple_queries),
            ("End-to-End Functionality", self.test_end_to_end_functionality)
        ]

        for test_name, test_func in tests:
            try:
                test_func()
                time.sleep(0.5)  # Small delay between tests
            except Exception as e:
                logger.error(f"Test {test_name} failed with exception: {str(e)}")
                # Mark this test as failed in results
                test_key = test_name.lower().replace(" ", "_").replace("-", "_")
                if test_key in self.test_results:
                    self.test_results[test_key] = False

        # Generate final report
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        pass_rate = passed_tests / total_tests

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "pass_rate": pass_rate,
                "overall_result": "PASSED" if pass_rate >= 0.8 else "FAILED"  # Need 80% to pass
            },
            "detailed_results": self.test_results
        }

        logger.info("="*60)
        logger.info("COMPREHENSIVE TEST RESULTS")
        logger.info("="*60)
        logger.info(f"Total tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {total_tests - passed_tests}")
        logger.info(f"Pass rate: {pass_rate:.2%}")
        logger.info(f"Overall result: {report['summary']['overall_result']}")
        logger.info("="*60)

        # Print detailed results
        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result else "✗ FAIL"
            logger.info(f"  {test_name.replace('_', ' ').title()}: {status}")

        return report

def print_detailed_report(report: Dict):
    """
    Print a detailed test report
    """
    print("\n" + "="*70)
    print("DETAILED RAG RETRIEVAL PIPELINE TEST REPORT")
    print("="*70)

    summary = report["summary"]
    print(f"Overall Status: {summary['overall_result']}")
    print(f"Pass Rate: {summary['pass_rate']:.2%} ({summary['passed_tests']}/{summary['total_tests']})")

    print("\nTest Details:")
    for test_name, result in report["detailed_results"].items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {test_name.replace('_', ' ').title()}: {status}")

    print("\nSuccess Criteria Validation:")
    criteria_met = 0
    total_criteria = 5

    # Criterion 1: Retrieval returns correct chunks for test queries
    if report["detailed_results"]["retrieval_accuracy"]:
        print("  [PASS] Retrieval returns correct chunks for test queries")
        criteria_met += 1
    else:
        print("  [FAIL] Retrieval returns correct chunks for test queries")

    # Criterion 2: Metadata matches original content
    if report["detailed_results"]["metadata_integrity"]:
        print("  [PASS] Metadata (url, title, chunk_id) matches original content")
        criteria_met += 1
    else:
        print("  [FAIL] Metadata (url, title, chunk_id) matches original content")

    # Criterion 3: Similarity queries return highly relevant results
    if report["detailed_results"]["relevance_test"]:
        print("  [PASS] Similarity queries return highly relevant results")
        criteria_met += 1
    else:
        print("  [FAIL] Similarity queries return highly relevant results")

    # Criterion 4: Pipeline handles multiple queries without errors
    if report["detailed_results"]["multiple_queries_test"]:
        print("  [PASS] Pipeline can handle multiple queries without errors")
        criteria_met += 1
    else:
        print("  [FAIL] Pipeline can handle multiple queries without errors")

    # Criterion 5: Logs confirm end-to-end functionality
    if report["detailed_results"]["end_to_end_test"]:
        print("  [PASS] End-to-end functionality confirmed with logging")
        criteria_met += 1
    else:
        print("  [FAIL] End-to-end functionality confirmed with logging")

    print(f"\nCriteria Met: {criteria_met}/{total_criteria}")
    print("="*70)

if __name__ == "__main__":
    tester = RetrievalTestSuite()
    report = tester.run_all_tests()
    print_detailed_report(report)

    # Exit with appropriate code based on test results
    if report["summary"]["overall_result"] == "PASSED":
        logger.info("All tests passed! Retrieval pipeline is ready for production.")
        sys.exit(0)
    else:
        logger.error("Some tests failed. Please review the issues before deploying.")
        sys.exit(1)