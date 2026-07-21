"""
Generates one interview question grounded in retrieved KB chunks.

Difficulty adapts to the previous answer's strength signal (see
interview_service.py) -- a lightweight, explainable adaptation rule
rather than a black-box scoring model, in line with "questions may
adapt based on previous responses (optional but valuable)".
"""
import json
import re
from typing import Dict, Any, List

from app.services.llm_client import get_client, is_llm_available

NEXT_DIFFICULTY = {
    "weak": "easy",
    "adequate": "medium",
    "strong": "hard",
    None: "medium",
}


def _llm_generate(
    role_label: str,
    topic: str,
    context_chunks: List[Dict[str, Any]],
    difficulty: str,
    profile: Dict[str, Any],
    already_asked: List[str],
) -> str:
    client = get_client()
    context_text = "\n---\n".join(c["text"] for c in context_chunks) or "(no retrieved context)"
    prompt = f"""You are conducting a structured technical interview for the role: {role_label}.

Candidate background: skills={profile.get('skills')}, domains={profile.get('domains')},
experience_level={profile.get('experience_level')}.

Retrieved knowledge-base context (ground the question in this, don't invent facts
outside it unless it's a general application of the concept):
{context_text[:3000]}

Focus topic for this question: {topic}
Target difficulty: {difficulty}
Already asked about: {already_asked}

Write exactly ONE interview question. Requirements:
- Specific and non-generic (no "tell me about yourself")
- Reflects conceptual or applied understanding of the retrieved context
- Difficulty matches the target level
- Do not repeat previously asked topics
- Return ONLY the question text, no preamble, no numbering, no quotes."""

    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in resp.content if b.type == "text").strip()
    return text.strip('"')


_TEMPLATES = {
    "easy": "In your own words, what is {topic} and why does it matter for a {role}?",
    "medium": "Walk me through how you would apply {topic} in a real {role} project, including one trade-off you'd consider.",
    "hard": "Design a solution involving {topic} for a {role} scenario with scale or reliability constraints, and justify your key decisions.",
}


def _fallback_generate(role_label: str, topic: str, difficulty: str) -> str:
    template = _TEMPLATES.get(difficulty, _TEMPLATES["medium"])
    return template.format(topic=topic, role=role_label)


def generate_question(
    role_label: str,
    topic: str,
    context_chunks: List[Dict[str, Any]],
    difficulty: str,
    profile: Dict[str, Any],
    already_asked: List[str],
) -> str:
    if is_llm_available():
        try:
            return _llm_generate(
                role_label, topic, context_chunks, difficulty, profile, already_asked
            )
        except Exception:
            return _fallback_generate(role_label, topic, difficulty)
    return _fallback_generate(role_label, topic, difficulty)


def score_answer_strength(answer_text: str) -> str:
    """Cheap heuristic used purely to steer next-question difficulty --
    NOT the final evaluation (that happens in the summary, optionally
    LLM-assisted with more context)."""
    words = len(answer_text.split())
    if words < 12:
        return "weak"
    if words < 40:
        return "adequate"
    return "strong"
