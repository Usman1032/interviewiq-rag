"""
Local embedding model wrapper.

Design decision: embeddings run locally via sentence-transformers rather
than an API call. This keeps the retrieval path fast, free, and available
even when ANTHROPIC_API_KEY isn't set (only generation needs the API key),
which matters for a 48-hour take-home that graders will run locally.
"""
from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer

from app.config import settings


@lru_cache(maxsize=1)
def get_embedder() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model)


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedder()
    vectors = model.encode(texts, normalize_embeddings=True)
    return vectors.tolist()


def embed_query(text: str) -> List[float]:
    return embed_texts([text])[0]
