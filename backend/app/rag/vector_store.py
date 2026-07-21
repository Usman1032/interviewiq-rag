"""
Thin wrapper around a persistent Chroma collection, one collection per
role. Isolating collections per role (rather than one big index with a
role metadata filter) keeps retrieval scoped and fast, and makes it
trivial to re-ingest a single role's corpus without touching the others.
"""
from typing import List, Dict, Any
import chromadb

from app.config import settings
from app.rag.embeddings import embed_texts, embed_query

_client = None


def get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.vector_store_dir)
    return _client


def get_collection(role_key: str):
    client = get_client()
    return client.get_or_create_collection(
        name=f"kb_{role_key}", metadata={"role_key": role_key}
    )


def upsert_chunks(role_key: str, chunks: List[Dict[str, Any]]) -> int:
    """
    chunks: list of {"id": str, "text": str, "source": str, "chunk_index": int}
    """
    if not chunks:
        return 0
    collection = get_collection(role_key)
    texts = [c["text"] for c in chunks]
    embeddings = embed_texts(texts)
    collection.upsert(
        ids=[c["id"] for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[
            {"source": c["source"], "chunk_index": c["chunk_index"]} for c in chunks
        ],
    )
    return len(chunks)


def query(role_key: str, query_text: str, top_k: int = None) -> List[Dict[str, Any]]:
    top_k = top_k or settings.top_k
    collection = get_collection(role_key)
    if collection.count() == 0:
        return []
    query_embedding = embed_query(query_text)
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(top_k, collection.count()),
    )
    hits = []
    for doc, meta, dist in zip(
        result["documents"][0], result["metadatas"][0], result["distances"][0]
    ):
        hits.append({"text": doc, "source": meta.get("source"), "score": 1 - dist})
    return hits
