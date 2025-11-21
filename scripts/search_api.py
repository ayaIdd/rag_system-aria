import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Search API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for loaded resources
model = None
index = None
metadata = None

class SearchRequest(BaseModel):
    query: str
    limit: int = 8
    threshold: float = 0.05

class SearchResult(BaseModel):
    id: str
    title: str
    date: str
    content: str
    similarity: float
    source: str

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total: int
    processing_time: float
    method: str

def load_resources():
    """Load model, index, and metadata into memory"""
    global model, index, metadata
    
    try:
        logger.info("Loading sentence transformer model...")
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        logger.info("Loading FAISS index...")
        index = faiss.read_index('lib/faiss_index.bin')
        
        logger.info("Loading metadata...")
        with open('lib/incident-metadata.json', 'r', encoding='utf-8') as f:
            metadata = json.load(f)
            
        logger.info("✅ All resources loaded successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to load resources: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    """Load resources when the application starts"""
    load_resources()

@app.get("/")
async def root():
    return {"message": "RAG Search API", "status": "ready"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if model and index and metadata:
        return {"status": "healthy", "model_loaded": True, "index_loaded": True}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")

@app.post("/search", response_model=SearchResponse)
async def search_incidents(request: SearchRequest):
    """Search for similar incidents"""
    start_time = time.time()
    
    if not model or not index or not metadata:
        raise HTTPException(status_code=503, detail="Search service not ready")
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        # Encode query
        query_embedding = model.encode([request.query])
        faiss.normalize_L2(query_embedding)
        
        # Search FAISS index
        scores, indices = index.search(query_embedding, request.limit)
        
        # Process results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if score < request.threshold:
                continue
                
            incident = metadata["incidents"][idx]
            results.append(SearchResult(
                id=incident["id"],
                title=incident["metadata"]["title"],
                date=incident["metadata"]["date"],
                content=incident["content"][:500] + "..." if len(incident["content"]) > 500 else incident["content"],
                similarity=float(score),
                source=incident["metadata"]["source"]
            ))
        
        processing_time = time.time() - start_time
        
        logger.info(f"Search: '{request.query}' -> {len(results)} results in {processing_time:.3f}s")
        
        return SearchResponse(
            query=request.query,
            results=results,
            total=len(results),
            processing_time=processing_time,
            method="faiss-semantic-search"
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get search system statistics"""
    if not metadata:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return {
        "total_incidents": metadata.get("total", 0),
        "embedding_dimension": metadata.get("dimension", 0),
        "model": metadata.get("model", "unknown"),
        "generated_at": metadata.get("generated_at", "unknown")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)