"""
Resume parsing / profile extraction.

Design decision: extraction is a two-step process --
  1. deterministic keyword matching against a curated skills taxonomy
     (fast, free, and gives predictable results to build queries from)
  2. if an API key is configured, a Claude call refines/dedupes/adds
     domain exposure that keyword matching alone would miss (e.g.
     inferring "distributed systems" exposure from project descriptions)
Both paths return the same shape, so downstream code never needs to know
which path ran.
"""
import io
import json
import re
from typing import Dict, Any, List

from pypdf import PdfReader

from app.config import settings
from app.services.llm_client import get_client, is_llm_available

SKILL_TAXONOMY = [
    "python", "java", "javascript", "typescript", "c++", "go", "rust",
    "fastapi", "flask", "django", "node.js", "express", "react", "next.js",
    "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "docker", "kubernetes", "aws", "gcp", "azure", "terraform", "ci/cd",
    "machine learning", "deep learning", "nlp", "computer vision",
    "pytorch", "tensorflow", "scikit-learn", "pandas", "numpy",
    "rag", "llm", "vector database", "embeddings", "transformers",
    "microservices", "rest api", "graphql", "system design",
    "data structures", "algorithms", "git", "linux", "kafka", "airflow",
]


def extract_text_from_pdf_bytes(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _keyword_extract(resume_text: str) -> List[str]:
    lower = resume_text.lower()
    found = []
    for skill in SKILL_TAXONOMY:
        if re.search(r"(?<![a-z])" + re.escape(skill) + r"(?![a-z])", lower):
            found.append(skill)
    return found


def _llm_refine_profile(resume_text: str, keyword_skills: List[str]) -> Dict[str, Any]:
    client = get_client()
    prompt = f"""You are extracting a structured candidate profile from a resume for a
technical interview system. Keyword matching already found these skills:
{keyword_skills}

Resume text:
---
{resume_text[:6000]}
---

Return ONLY valid JSON (no prose, no markdown fences) with this exact shape:
{{
  "skills": ["..."],
  "technologies": ["..."],
  "domains": ["..."],
  "experience_level": "junior|mid|senior",
  "notable_projects": ["short phrase", "..."]
}}
"skills" should merge and clean up the keyword list above with anything else evident
in the resume. "domains" means broader areas like "backend systems", "recommender
systems", "data pipelines" -- inferred from context, not just keyword matches."""

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = "".join(b.text for b in resp.content if b.type == "text").strip()
    raw = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(raw)


def _fallback_profile(keyword_skills: List[str]) -> Dict[str, Any]:
    return {
        "skills": keyword_skills,
        "technologies": keyword_skills,
        "domains": [],
        "experience_level": "unknown",
        "notable_projects": [],
    }


def extract_profile(resume_text: str) -> Dict[str, Any]:
    keyword_skills = _keyword_extract(resume_text)
    if is_llm_available():
        try:
            return _llm_refine_profile(resume_text, keyword_skills)
        except Exception:
            # Never let a flaky LLM call break resume upload -- degrade gracefully.
            return _fallback_profile(keyword_skills)
    return _fallback_profile(keyword_skills)
