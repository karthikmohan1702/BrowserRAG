# coding: utf-8
"""
Main FastAPI agent application for vector store assistant.
"""

import os
import faiss
import numpy as np
import requests as req
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
from backend.memory import MemoryManager
from backend.decision import generate_summary, parse_llm_json
from backend.action import log_page_action, search_action

# Explicitly load .env from the backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = FastAPI()

# Initialize memory manager (handles embeddings and FAISS)
memory_manager = MemoryManager()

class URLRequest(BaseModel):
    """URLRequest model for URL requests."""
    url: str

class DeletePageRequest(BaseModel):
    """DeletePageRequest model for deleting pages."""
    url: str

class SearchRequest(BaseModel):
    """SearchRequest model for search queries."""
    query: str
    k: int = 5

class SummaryRequest(BaseModel):
    """SummaryRequest model for summary requests."""
    url: str

@app.post("/log_page")
async def log_page(request: Request):
    """
    Log a page and its HTML content.

    Args:
    request (Request): The incoming request with URL and HTML content.

    Returns:
    The result of logging the page action.
    """
    data = await request.json()
    url = data["url"]
    html = data.get("html")
    if not html:
        # Fetch HTML if not provided
        resp = req.get(url)
        resp.raise_for_status()
        html = resp.text
    return await log_page_action(html, url, memory_manager, "http://127.0.0.1:3001/sse")

@app.post("/user_query")
async def user_query(request: SearchRequest):
    """
    Handle a user query.

    Args:
    request (SearchRequest): The incoming search request with query and k.

    Returns:
    The result of the search action.
    """
    query = request.query
    k = request.k
    return search_action(query, memory_manager, k)

@app.post("/summary")
async def summary(request: SummaryRequest):
    """
    Generate a summary for a given URL.

    Args:
    request (SummaryRequest): The incoming summary request with URL.

    Returns:
    The generated summary for the URL.
    """
    url = request.url
    # Find all chunks for the url
    chunks = [c["chunk"] for c in memory_manager.chunks if c["url"] == url]
    if not chunks:
        return {"error": "No content found for this URL. Please index it first."}
    context = "\n\n".join(chunks)
    summary_text = generate_summary(context)
    return {"url": url, "summary": summary_text}

@app.post("/search")
async def search(request: Request):
    """
    Handle a search query.

    Args:
    request (Request): The incoming search request with query and k.

    Returns:
    The result of the search action.
    """
    data = await request.json()
    query = data["query"]
    k = data.get("k", 5)
    return search_action(query, memory_manager, k)

@app.post("/convert")
async def convert_url_to_markdown(request: URLRequest):
    """
    Convert a URL to Markdown.

    Args:
    request (URLRequest): The incoming URL request.

    Returns:
    The Markdown content for the URL.
    """
    markdown = await extract_markdown(request.url)
    return {"markdown": markdown}

@app.get("/list_pages")
async def list_pages():
    """
    List all unique URLs indexed.

    Returns:
    A list of unique URLs.
    """
    # Return unique URLs indexed
    urls = list({c["url"] for c in memory_manager.chunks})
    return {"urls": urls}

@app.post("/delete_page")
async def delete_page(request: DeletePageRequest):
    """
    Delete a page and its associated chunks.

    Args:
    request (DeletePageRequest): The incoming delete page request with URL.

    Returns:
    The result of deleting the page.
    """
    url = request.url
    # Remove all chunks for this URL and rebuild index
    old_indices = [i for i, c in enumerate(memory_manager.chunks) if c["url"] == url]
    if not old_indices:
        return {"status": "not_found", "url": url}
    keep_indices = [i for i in range(len(memory_manager.chunks)) if i not in old_indices]
    if keep_indices:
        kept_embs = [memory_manager.chunks[i]["embedding"] for i in keep_indices]
        memory_manager.index = faiss.IndexFlatL2(memory_manager.model.get_sentence_embedding_dimension())
        if kept_embs:
            memory_manager.index.add(np.array(kept_embs).astype('float32'))
        memory_manager.chunks = [memory_manager.chunks[i] for i in keep_indices]
    else:
        memory_manager.index = faiss.IndexFlatL2(memory_manager.model.get_sentence_embedding_dimension())
        memory_manager.chunks = []
    memory_manager._save_index()
    return {"status": "deleted", "url": url}

@app.get("/health")
async def health():
    """
    Check the health of the application.

    Returns:
    The health status of the application.
    """
    # Check if embedding model and FAISS index are loaded
    try:
        dim = memory_manager.model.get_sentence_embedding_dimension()
        num_vecs = memory_manager.index.ntotal
        return {"status": "ok", "embedding_model_dim": dim, "faiss_vectors": num_vecs}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.get("/faiss_stats")
async def faiss_stats():
    """
    Get FAISS statistics.

    Returns:
    FAISS statistics.
    """
    try:
        dim = memory_manager.model.get_sentence_embedding_dimension()
        num_vecs = memory_manager.index.ntotal
        return {
            "faiss_vectors": num_vecs,
            "embedding_dim": dim,
            "num_chunks": len(memory_manager.chunks),
            "faiss_index_type": type(memory_manager.index).__name__
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}
