"""
Knowledge ingestion: load role-specific source docs (.txt or .pdf),
chunk them with overlap, and push them into the vector store.

Chunking strategy: fixed-size character windows with overlap. This is a
simple, dependency-light choice that still preserves context across chunk
boundaries (the overlap) -- appropriate for a 48-hour build. The chunk
size/overlap are configurable via env vars so they can be tuned per
corpus without code changes.
"""
import os
from typing import List, Dict, Any

from pypdf import PdfReader

from app.config import settings
from app.rag.vector_store import upsert_chunks


def _read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _read_pdf_file(path: str) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def load_document(path: str) -> str:
    if path.lower().endswith(".pdf"):
        return _read_pdf_file(path)
    return _read_text_file(path)


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    text = " ".join(text.split())  # normalize whitespace
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def ingest_role(role_key: str) -> int:
    """Ingest every document under knowledge_base_dir/<role_key>/ into the
    vector store collection for that role. Returns number of chunks stored."""
    role_dir = os.path.join(settings.knowledge_base_dir, role_key)
    if not os.path.isdir(role_dir):
        raise FileNotFoundError(f"No knowledge base folder for role '{role_key}': {role_dir}")

    all_chunks: List[Dict[str, Any]] = []
    for fname in sorted(os.listdir(role_dir)):
        if not fname.lower().endswith((".txt", ".pdf")):
            continue
        fpath = os.path.join(role_dir, fname)
        text = load_document(fpath)
        pieces = chunk_text(text)
        for idx, piece in enumerate(pieces):
            all_chunks.append(
                {
                    "id": f"{role_key}:{fname}:{idx}",
                    "text": piece,
                    "source": fname,
                    "chunk_index": idx,
                }
            )

    return upsert_chunks(role_key, all_chunks)


def ingest_all_roles(role_keys: List[str]) -> Dict[str, int]:
    return {role_key: ingest_role(role_key) for role_key in role_keys}
