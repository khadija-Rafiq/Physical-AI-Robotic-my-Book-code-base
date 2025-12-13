from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
import cohere

load_dotenv()

app = FastAPI(title="RAG Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENV
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

if not COHERE_API_KEY:
    raise RuntimeError("COHERE_API_KEY missing")

# Clients
co = cohere.Client(COHERE_API_KEY)

qdrant = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    https=True
)

# Models
class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@app.get("/")
def home():
    return {"message": "RAG Backend Running ✔"}

@app.post("/query")
def query_rag(data: QueryRequest):
    try:
        # 1️⃣ Embed query
        embedding = co.embed(
            texts=[data.query],
            model="embed-multilingual-v3.0",
            input_type="search_query"
        ).embeddings[0]

        # 2️⃣ Qdrant search (NEW API)
        result = qdrant.query_points(
            collection_name="rag_embedding",
            query=embedding,
            limit=data.top_k,
            with_payload=True
        )

        # 3️⃣ Format output
        answers = []
        for point in result.points:
            answers.append({
                "score": point.score,
                "text": point.payload.get("text", ""),
                "source": point.payload.get("source_url", "")
            })

        return {
            "query": data.query,
            "results": answers
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))












# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# import os
# from dotenv import load_dotenv
# from qdrant_client import QdrantClient
# from qdrant_client.http import models
# import cohere

# load_dotenv()

# app = FastAPI()

# # CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Load keys
# COHERE_API_KEY = os.getenv("COHERE_API_KEY")
# QDRANT_URL = os.getenv("QDRANT_URL")
# QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# co = cohere.Client(COHERE_API_KEY)

# # Connect to Qdrant
# qdrant = QdrantClient(
#     url=QDRANT_URL,
#     api_key=QDRANT_API_KEY,
#     https=True
# )

# class QueryRequest(BaseModel):
#     query: str

# @app.get("/")
# def home():
#     return {"message": "RAG Backend Running ✔"}

# @app.post("/query")
# def search_query(data: QueryRequest):
#     try:
#         query_embedding = co.embed(
#             texts=[data.query],
#             model="embed-multilingual-v3.0",
#             input_type="search_query"
#         ).embeddings[0]

#         results = qdrant.search(
#             collection_name="rag_embedding",
#             query_vector=query_embedding,
#             limit=5
#         )

#         output = []
#         for r in results:
#             output.append({
#                 "score": r.score,
#                 "text": r.payload.get("text", "")
#             })

#         return {"results": output}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))











