"""
Relevance Testing for RAG Pipeline
Module for testing the relevance of retrieved results
"""
import os
import logging
from typing import List, Dict
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

class RelevanceTester:
    def __init__(self, collection_name: str = "rag_embedding"):
        self.collection_name = collection_name
        self.client = qdrant_client

    def test_query_relevance(self, query: str, expected_keywords: List[str] = None) -> Dict:
        """
        Test the relevance of results for a specific query
        """
        logger.info(f"Testing relevance for query: '{query}'")

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

            # Analyze relevance
            relevance_analysis = {
                "query": query,
                "total_results": len(search_results),
                "relevant_results": 0,
                "results": []
            }

            for result in search_results:
                result_text = result.payload.get("text", "").lower()
                result_score = result.score

                # Check for expected keywords if provided
                keyword_matches = 0
                if expected_keywords:
                    for keyword in expected_keywords:
                        if keyword.lower() in result_text:
                            keyword_matches += 1

                # Determine if result is relevant based on keywords or score
                is_relevant = keyword_matches > 0 or result_score > 0.5

                if is_relevant:
                    relevance_analysis["relevant_results"] += 1

                relevance_analysis["results"].append({
                    "id": result.id,
                    "score": result_score,
                    "text_preview": result_text[:100] + "..." if len(result_text) > 100 else result_text,
                    "source_url": result.payload.get("source_url", ""),
                    "keyword_matches": keyword_matches,
                    "is_relevant": is_relevant
                })

            logger.info(f"Query '{query}' returned {relevance_analysis['relevant_results']}/{relevance_analysis['total_results']} relevant results")
            return relevance_analysis

        except Exception as e:
            logger.error(f"Error testing query relevance: {str(e)}")
            return {"query": query, "error": str(e)}

    def calculate_relevance_metrics(self, queries_with_expected: List[Dict]) -> Dict:
        """
        Calculate overall relevance metrics across multiple queries
        """
        logger.info("Calculating overall relevance metrics...")

        total_queries = len(queries_with_expected)
        total_results = 0
        relevant_results = 0
        avg_score = 0

        for query_data in queries_with_expected:
            query = query_data["query"]
            expected_keywords = query_data.get("expected_keywords", [])

            analysis = self.test_query_relevance(query, expected_keywords)
            if "error" not in analysis:
                total_results += analysis["total_results"]
                relevant_results += analysis["relevant_results"]

        if total_results > 0:
            relevance_ratio = relevant_results / total_results
        else:
            relevance_ratio = 0

        metrics = {
            "total_queries": total_queries,
            "total_results": total_results,
            "relevant_results": relevant_results,
            "relevance_ratio": relevance_ratio,
            "relevance_percentage": relevance_ratio * 100
        }

        logger.info(f"Relevance metrics: {metrics['relevance_percentage']:.2f}% of results were relevant")
        return metrics

    def run_relevance_tests(self) -> Dict:
        """
        Run comprehensive relevance tests
        """
        logger.info("Running comprehensive relevance tests...")

        # Define test queries with expected keywords
        test_queries = [
            {
                "query": "Physical AI and Robotics",
                "expected_keywords": ["physical", "ai", "robotics", "robot"]
            },
            {
                "query": "Humanoid Robotics Foundations",
                "expected_keywords": ["humanoid", "robotics", "foundations", "movement"]
            },
            {
                "query": "What is Physical AI?",
                "expected_keywords": ["physical", "ai", "artificial", "intelligence"]
            },
            {
                "query": "Introduction to the book",
                "expected_keywords": ["introduction", "book", "overview", "chapters"]
            },
            {
                "query": "Machine learning in robotics",
                "expected_keywords": ["machine", "learning", "robotics", "algorithms"]
            }
        ]

        results = {
            "queries_tested": len(test_queries),
            "query_analyses": [],
            "metrics": {}
        }

        for query_data in test_queries:
            analysis = self.test_query_relevance(query_data["query"], query_data["expected_keywords"])
            results["query_analyses"].append(analysis)

        # Calculate overall metrics
        results["metrics"] = self.calculate_relevance_metrics(test_queries)

        return results

def print_relevance_report(report: Dict):
    """
    Print a formatted relevance test report
    """
    print("\n" + "="*60)
    print("RELEVANCE TEST REPORT")
    print("="*60)

    print(f"Total queries tested: {report['queries_tested']}")
    print(f"Total results: {report['metrics']['total_results']}")
    print(f"Relevant results: {report['metrics']['relevant_results']}")
    print(f"Relevance ratio: {report['metrics']['relevance_ratio']:.2f} ({report['metrics']['relevance_percentage']:.2f}%)")

    print("\nDetailed Query Results:")
    for i, analysis in enumerate(report['query_analyses']):
        if "error" not in analysis:
            print(f"\n  Query {i+1}: '{analysis['query']}'")
            print(f"    Results: {analysis['relevant_results']}/{analysis['total_results']} relevant")

            # Show top result
            if analysis['results']:
                top_result = analysis['results'][0]
                print(f"    Top result score: {top_result['score']:.3f}")
                print(f"    Top result preview: {top_result['text_preview'][:100]}...")

    print("="*60)

if __name__ == "__main__":
    tester = RelevanceTester()

    # Run relevance tests
    relevance_report = tester.run_relevance_tests()
    print_relevance_report(relevance_report)