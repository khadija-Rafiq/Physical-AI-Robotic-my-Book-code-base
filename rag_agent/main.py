"""
RAG Agent Backend using OpenAIAgentSDK and FastAPI
Main application entry point
"""
import os
import logging
from typing import List, Dict, Optional, Union
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import uvicorn
from qdrant_client import QdrantClient
from qdrant_client.http import models
import cohere
import openai
import asyncio
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize clients
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")  # For cloud instance
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
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

# Pydantic models
class QuestionRequest(BaseModel):
    question: str
    top_k: int = 5
    max_tokens: int = 500

class AnswerResponse(BaseModel):
    question: str
    answer: str
    retrieved_chunks: List[Dict]
    retrieval_metadata: Dict
    timestamp: str

class HealthCheck(BaseModel):
    status: str
    timestamp: str

# Initialize FastAPI app
app = FastAPI(
    title="RAG Agent Backend",
    description="RAG Agent using OpenAIAgentSDK and FastAPI for question-answering based on book content",
    version="0.1.0"
)

import threading
from concurrent.futures import ThreadPoolExecutor
import time

class RAGAgent:
    """
    RAG Agent class that handles the retrieval and generation process
    """
    def __init__(self, collection_name: str = "rag_embedding"):
        self.collection_name = collection_name
        self.qdrant_client = qdrant_client
        self.cohere_client = cohere_client
        self.request_counter = 0
        self.request_lock = threading.Lock()

    async def retrieve_chunks(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant chunks from Qdrant based on the query
        """
        logger.info(f"Retrieving chunks for query: '{query}' (top-{top_k})")

        try:
            # Generate embedding for the query
            response = self.cohere_client.embed(
                texts=[query],
                model="embed-multilingual-v3.0",
                input_type="search_query"  # Optimize for search queries
            )
            query_embedding = response.embeddings[0]

            # Perform similarity search using query_points for newer Qdrant client
            search_response = self.qdrant_client.query_points(
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

            logger.info(f"Retrieved {len(formatted_results)} chunks for query: '{query}'")
            return formatted_results

        except Exception as e:
            logger.error(f"Error retrieving chunks for query '{query}': {str(e)}")
            return []

    def generate_answer(self, question: str, context_chunks: List[Dict], max_tokens: int = 500) -> str:
        """
        Generate an answer based on the question and retrieved context
        """
        logger.info(f"Generating answer for question: '{question}'")

        # Combine context chunks into a single context string, prioritizing higher scoring chunks
        # Sort chunks by score in descending order to prioritize most relevant content
        sorted_chunks = sorted(context_chunks, key=lambda x: x.get("score", 0), reverse=True)

        context_texts = []
        total_chars = 0
        max_context_chars = 3000  # Limit context to prevent token overflow

        for chunk in sorted_chunks:
            if chunk.get("text"):
                chunk_text = chunk["text"]
                # Add chunk if it doesn't exceed our context limit
                if total_chars + len(chunk_text) <= max_context_chars:
                    context_texts.append(f"Source: {chunk.get('source_url', 'Unknown')}\nContent: {chunk_text}")
                    total_chars += len(chunk_text)
                else:
                    # Add partial chunk if there's remaining space
                    remaining_chars = max_context_chars - total_chars
                    if remaining_chars > 0:
                        partial_chunk = chunk_text[:remaining_chars]
                        context_texts.append(f"Source: {chunk.get('source_url', 'Unknown')}\nContent: {partial_chunk}...")
                        break

        context = "\n\n".join(context_texts)

        # Create a message for the language model with better instructions
        messages = [
            {
                "role": "system",
                "content": """You are an expert assistant for the Physical AI Robotics book.
                Your role is to provide accurate answers based only on the provided context.
                - Use only information from the context to answer questions
                - If the answer cannot be found in the context, clearly state this
                - Be concise but comprehensive in your responses
                - Cite sources when possible by referencing the provided URLs"""
            },
            {
                "role": "user",
                "content": f"""
                Please answer the following question based only on the provided context.

                Question: {question}

                Context: {context}

                Provide a detailed and accurate answer based on the context provided.
                If the answer cannot be found in the context, please state that clearly.
                """
            }
        ]

        try:
            # Use OpenAI's chat completion API to create the answer
            response = openai_client.chat.completions.create(
                model="gpt-4o",  # Using a high-quality model
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for more consistent answers
                top_p=0.9,  # Use nucleus sampling for better quality
            )

            answer = response.choices[0].message.content.strip()
            logger.info(f"Generated answer with {len(answer)} characters")
            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return "Sorry, I encountered an error while generating the answer. Please try again."

    async def process_query(self, question: str, top_k: int = 5, max_tokens: int = 500) -> Dict:
        """
        Process a query end-to-end: retrieve relevant chunks and generate an answer
        """
        start_time = datetime.now()

        # Thread-safe request counting
        with self.request_lock:
            self.request_counter += 1
            request_id = self.request_counter

        logger.info(f"[Request-{request_id}] Processing query: '{question}'")

        # Log the retrieval → answer flow
        retrieval_start = datetime.now()
        logger.info(f"[Request-{request_id}] Step 1: Retrieving relevant chunks")

        # Step 1: Retrieve relevant chunks
        retrieved_chunks = await self.retrieve_chunks(question, top_k)

        retrieval_time = (datetime.now() - retrieval_start).total_seconds()
        logger.info(f"[Request-{request_id}] Retrieved {len(retrieved_chunks)} chunks in {retrieval_time:.2f}s")

        # Step 2: Generate answer based on retrieved chunks
        generation_start = datetime.now()
        logger.info(f"[Request-{request_id}] Step 2: Generating answer from {len(retrieved_chunks)} chunks")

        answer = self.generate_answer(question, retrieved_chunks, max_tokens)

        generation_time = (datetime.now() - generation_start).total_seconds()
        logger.info(f"[Request-{request_id}] Generated answer in {generation_time:.2f}s")

        # Step 3: Prepare metadata
        retrieval_metadata = {
            "request_id": request_id,
            "retrieval_time": retrieval_time,
            "generation_time": generation_time,
            "total_processing_time": (datetime.now() - start_time).total_seconds(),
            "chunks_retrieved": len(retrieved_chunks),
            "avg_score": sum([chunk["score"] for chunk in retrieved_chunks]) / len(retrieved_chunks) if retrieved_chunks else 0,
            "query_timestamp": start_time.isoformat(),
            "context_chars": sum(len(chunk.get("text", "")) for chunk in retrieved_chunks)
        }

        logger.info(f"[Request-{request_id}] Query processing completed. Total time: {retrieval_metadata['total_processing_time']:.2f}s")
        logger.info(f"[Request-{request_id}] Retrieval → Answer flow completed successfully")

        return {
            "question": question,
            "answer": answer,
            "retrieved_chunks": retrieved_chunks,
            "retrieval_metadata": retrieval_metadata
        }

# Initialize the RAG agent
rag_agent = RAGAgent()

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check endpoint
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )

@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    """
    Main endpoint to ask a question and get an answer based on book content
    """
    try:
        # Process the query using the RAG agent
        result = await rag_agent.process_query(
            question=request.question,
            top_k=request.top_k,
            max_tokens=request.max_tokens
        )

        return AnswerResponse(
            question=result["question"],
            answer=result["answer"],
            retrieved_chunks=result["retrieved_chunks"],
            retrieval_metadata=result["retrieval_metadata"],
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error processing question '{request.question}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/collections")
async def list_collections():
    """
    List available Qdrant collections
    """
    try:
        collections = qdrant_client.get_collections()
        return {"collections": [col.name for col in collections.collections]}
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing collections: {str(e)}")

@app.get("/stats")
async def get_stats():
    """
    Get statistics about the RAG agent performance
    """
    try:
        # Get collection info
        collection_info = qdrant_client.get_collection(rag_agent.collection_name)

        stats = {
            "collection_name": rag_agent.collection_name,
            "vectors_count": collection_info.points_count,
            "request_count": rag_agent.request_counter,
            "timestamp": datetime.now().isoformat()
        }
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")

@app.post("/test_concurrent")
async def test_concurrent_requests(requests: List[QuestionRequest]):
    """
    Test concurrent request handling by processing multiple requests at once
    """
    start_time = datetime.now()
    logger.info(f"Processing {len(requests)} concurrent requests")

    # Process requests concurrently
    import asyncio
    tasks = []
    for req in requests:
        task = rag_agent.process_query(req.question, req.top_k, req.max_tokens)
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Handle any exceptions in the results
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Error in request {i}: {str(result)}")
            processed_results.append({
                "question": requests[i].question,
                "error": str(result)
            })
        else:
            processed_results.append(result)

    total_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"Processed {len(requests)} concurrent requests in {total_time:.2f}s")

    return {
        "total_requests": len(requests),
        "successful_requests": len([r for r in results if not isinstance(r, Exception)]),
        "failed_requests": len([r for r in results if isinstance(r, Exception)]),
        "total_time": total_time,
        "results": processed_results
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )












