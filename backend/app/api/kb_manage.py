"""Knowledge Base Management API — upload, search, manage insurance knowledge."""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.app.core.config import settings
from backend.app.services.knowledge_base import get_knowledge_base, COLLECTIONS
from backend.app.services.chunker import chunk_file_content
from backend.app.utils.pdf_utils import extract_text

router = APIRouter()


class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    top_k: int = 5


class AddTextRequest(BaseModel):
    text: str
    category: str = "policy_clauses"
    source: str = "manual_input"


@router.get("/stats")
async def kb_stats():
    """Get knowledge base statistics."""
    kb = get_knowledge_base()
    return {"stats": kb.get_stats(), "total_categories": len(COLLECTIONS)}


@router.get("/categories")
async def kb_categories():
    """List all knowledge categories."""
    return {
        "categories": [
            {"key": k, "name": v} for k, v in COLLECTIONS.items()
        ]
    }


@router.post("/upload")
async def upload_to_kb(
    file: UploadFile = File(...),
    category: str = Form("policy_clauses"),
    source: str = Form(""),
):
    """Upload a document to the knowledge base. Supports PDF, DOCX, TXT, MD."""
    if category not in COLLECTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}. Available: {list(COLLECTIONS.keys())}")

    # Save file
    ext = os.path.splitext(file.filename or "doc.txt")[1]
    file_id = uuid.uuid4().hex[:8]
    file_path = os.path.join(settings.upload_dir, f"kb_{file_id}_{file.filename}")
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Extract text
    try:
        text = extract_text(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {e}")

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="No text content found in file")

    # Chunk
    chunks = chunk_file_content(text, file.filename or "document")
    if not chunks:
        raise HTTPException(status_code=400, detail="No valid chunks extracted")

    # Add to knowledge base
    kb = get_knowledge_base()
    src = source or file.filename or f"upload_{file_id}"
    count = kb.add_documents(
        texts=chunks,
        category=category,
        source=src,
    )

    return {
        "status": "ok",
        "filename": file.filename,
        "chunks_added": count,
        "category": category,
        "source": src,
        "text_length": len(text),
        "preview": text[:300] + "..." if len(text) > 300 else text,
    }


@router.post("/add-text")
async def add_text_to_kb(req: AddTextRequest):
    """Add raw text to the knowledge base."""
    if req.category not in COLLECTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid category: {req.category}")

    chunks = chunk_file_content(req.text, req.source or "text_input")
    if not chunks:
        raise HTTPException(status_code=400, detail="No valid chunks extracted")

    kb = get_knowledge_base()
    count = kb.add_documents(
        texts=chunks,
        category=req.category,
        source=req.source or "manual_input",
    )

    return {
        "status": "ok",
        "chunks_added": count,
        "category": req.category,
        "text_length": len(req.text),
    }


@router.post("/search")
async def search_kb(req: SearchRequest):
    """Semantic search across the knowledge base."""
    kb = get_knowledge_base()
    result = kb.search(
        query=req.query,
        top_k=req.top_k,
        category=req.category,
    )

    return {
        "query": req.query,
        "total_found": result.total_found,
        "results": [
            {
                "content": c.content,
                "source": c.source,
                "category": c.category,
                "score": c.relevance_score,
                "category_name": COLLECTIONS.get(c.category, c.category),
            }
            for c in result.chunks
        ],
    }


@router.post("/seed")
async def seed_kb():
    """Re-seed the knowledge base with built-in insurance knowledge data."""
    from backend.app.services.seed_knowledge import seed_knowledge_base
    stats = seed_knowledge_base()
    total = sum(stats.values())
    return {"status": "seeded", "total_chunks": total, "by_category": stats}


@router.delete("/clear/{category}")
async def clear_category(category: str):
    """Clear all documents in a category. Use with caution."""
    if category not in COLLECTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")

    kb = get_knowledge_base()
    try:
        coll = kb._chroma_client.get_collection(category)
        count = coll.count()
        # ChromaDB doesn't have a simple clear(), so we delete and recreate
        kb._chroma_client.delete_collection(category)
        kb._chroma_client.create_collection(
            name=category,
            metadata={"description": COLLECTIONS[category], "hnsw:space": "cosine"},
        )
        return {"status": "cleared", "category": category, "documents_removed": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
