"""Single shared Anthropic client + availability check, so every service
that needs the LLM (resume refinement, question generation, summaries)
degrades the same way when no API key is configured."""
from functools import lru_cache
import anthropic

from app.config import settings


def is_llm_available() -> bool:
    return bool(settings.anthropic_api_key)


@lru_cache(maxsize=1)
def get_client() -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)
