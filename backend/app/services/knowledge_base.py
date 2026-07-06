"""Insurance Knowledge Base — RAG service for semantic retrieval.

Architecture:
  Documents → Chunk → Embed (千问 text-embedding-v2, 1536d) → ChromaDB
  Query → Embed → Semantic Search → Top-K Results → Inject into Agent Prompt

Embedding: 阿里千问 text-embedding-v2 — 中文语义检索 SOTA
"""

import os
import uuid
import time
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

import chromadb
from chromadb.config import Settings as ChromaSettings

from backend.app.core.config import settings


# ChromaDB persistence directory
CHROMA_PATH = Path(settings.output_dir).parent / "chroma_db"
CHROMA_PATH.mkdir(parents=True, exist_ok=True)

# Collection names
COLLECTIONS = {
    "policy_clauses": "保单条款库 — 标准条款、保障范围、除外责任",
    "underwriting_guides": "核保指南库 — 行业承保偏好、费率基准、红线",
    "claims_rules": "理赔规则库 — 判定标准、准备金计算、欺诈指标",
    "regulations": "监管法规库 — 保监会规定、行业合规",
    "industry_benchmarks": "行业基准库 — 风险因子、费率区间、损失率",
}


@dataclass
class KnowledgeChunk:
    """A retrieved knowledge chunk with metadata."""
    content: str
    source: str = ""
    category: str = ""
    relevance_score: float = 0.0
    chunk_id: str = ""


@dataclass
class SearchResult:
    """Complete search results from knowledge base."""
    chunks: list[KnowledgeChunk] = field(default_factory=list)
    query: str = ""
    total_found: int = 0


class KnowledgeBase:
    """Insurance domain knowledge base with semantic search.
    Uses 千问 text-embedding-v2 for embeddings (best Chinese semantic retrieval).
    """

    QWEN_EMBED_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"

    def __init__(self, embedding_model: str = "text-embedding-v2"):
        self.embedding_model = embedding_model

        self._chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_PATH),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        self._ensure_collections()

    def _ensure_collections(self):
        """Create collections if they don't exist."""
        for name in COLLECTIONS:
            try:
                self._chroma_client.get_collection(name)
            except Exception:
                self._chroma_client.create_collection(
                    name=name,
                    metadata={"description": COLLECTIONS[name], "hnsw:space": "cosine"},
                )

    def _get_collection(self, category: Optional[str] = None) -> list:
        """Get one or all collections."""
        if category and category in COLLECTIONS:
            return [self._chroma_client.get_collection(category)]
        return [self._chroma_client.get_collection(name) for name in COLLECTIONS]

    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings using 千问 text-embedding-v2 API."""
        import requests

        all_embeddings = []
        batch_size = 10  # 千问建议批次大小

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            resp = requests.post(
                self.QWEN_EMBED_URL,
                headers={
                    "Authorization": f"Bearer {settings.qwen_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.embedding_model,
                    "input": batch,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

            # 千问返回格式: {"data": [{"embedding": [...], "index": 0}, ...]}
            for item in sorted(data["data"], key=lambda x: x["index"]):
                all_embeddings.append(item["embedding"])

            # Rate limit protection
            if i + batch_size < len(texts):
                time.sleep(0.1)

        return all_embeddings

    def add_documents(
        self,
        texts: list[str],
        category: str = "policy_clauses",
        source: str = "",
        metadatas: Optional[list[dict]] = None,
    ) -> int:
        """Add documents to the knowledge base. Returns number of chunks added."""
        if category not in COLLECTIONS:
            raise ValueError(f"Unknown category: {category}. Available: {list(COLLECTIONS.keys())}")

        collection = self._chroma_client.get_collection(category)

        # Generate IDs and embeddings
        ids = [f"kb_{uuid.uuid4().hex[:12]}" for _ in texts]
        embeddings = self._embed(texts)

        if metadatas is None:
            metadatas = [{"source": source, "category": category} for _ in texts]
        else:
            for m in metadatas:
                m.setdefault("source", source)
                m.setdefault("category", category)

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return len(ids)

    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        min_score: float = 0.3,
    ) -> SearchResult:
        """Semantic search across the knowledge base."""
        query_embedding = self._embed([query])[0]

        # Search across specified collections
        if category:
            collections_to_search = [self._chroma_client.get_collection(category)]
        else:
            collections_to_search = [
                self._chroma_client.get_collection(name) for name in COLLECTIONS
            ]

        all_results = []
        for coll in collections_to_search:
            try:
                results = coll.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                )
                if results["ids"] and results["ids"][0]:
                    for i, chunk_id in enumerate(results["ids"][0]):
                        distance = results["distances"][0][i] if results.get("distances") else [0]
                        # Cosine distance to similarity score
                        score = 1.0 - min(distance[0] if isinstance(distance, list) else distance, 1.0)

                        if score >= min_score:
                            all_results.append(KnowledgeChunk(
                                content=results["documents"][0][i],
                                source=results["metadatas"][0][i].get("source", ""),
                                category=results["metadatas"][0][i].get("category", category or ""),
                                relevance_score=round(score, 4),
                                chunk_id=chunk_id,
                            ))
            except Exception as e:
                continue

        # Sort by relevance and deduplicate
        all_results.sort(key=lambda x: x.relevance_score, reverse=True)
        seen = set()
        unique_results = []
        for r in all_results:
            content_key = r.content[:100]
            if content_key not in seen:
                seen.add(content_key)
                unique_results.append(r)

        return SearchResult(
            chunks=unique_results[:top_k],
            query=query,
            total_found=len(unique_results),
        )

    def format_for_prompt(self, search_result: SearchResult, max_chars: int = 3000) -> str:
        """Format search results as a structured prompt context."""
        if not search_result.chunks:
            return ""

        lines = ["## 📚 知识库检索结果（基于真实保险知识）\n"]
        lines.append(f"以下是从知识库中检索到的 {len(search_result.chunks)} 条相关知识：\n")

        total_chars = 0
        for i, chunk in enumerate(search_result.chunks, 1):
            cat_name = COLLECTIONS.get(chunk.category, chunk.category)
            header = f"### [{i}] {cat_name}（相关度: {chunk.relevance_score:.0%}）"
            source_info = f"\n> 来源: {chunk.source}" if chunk.source else ""

            block = f"{header}{source_info}\n{chunk.content}\n"
            if total_chars + len(block) > max_chars:
                lines.append(f"\n*(共检索到 {search_result.total_found} 条结果，已截断显示前 {i-1} 条)*")
                break
            lines.append(block)
            total_chars += len(block)

        lines.append("\n---")
        lines.append("⚠️ 请基于以上知识库内容进行分析，并在输出中引用相关知识来源。\n")
        return "\n".join(lines)

    def get_stats(self) -> dict:
        """Get knowledge base statistics."""
        stats = {}
        for name in COLLECTIONS:
            try:
                coll = self._chroma_client.get_collection(name)
                stats[name] = {
                    "description": COLLECTIONS[name],
                    "documents": coll.count(),
                }
            except Exception:
                stats[name] = {"description": COLLECTIONS[name], "documents": 0}
        return stats


# Global singleton
_kb_instance: Optional[KnowledgeBase] = None


def get_knowledge_base() -> KnowledgeBase:
    """Get or create the global knowledge base instance."""
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
