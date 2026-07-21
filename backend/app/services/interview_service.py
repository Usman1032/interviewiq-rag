"""
Orchestrates the full interview lifecycle:
  Context Construction -> Retrieval -> Question Generation -> Storage
  -> Answer Handling -> next-question adaptation -> Summary

This is the module the API routers call into; it owns no HTTP concerns,
only business logic, per the "clear separation of responsibilities"
expectation in section 5.
"""
import json
import re
from typing import List

from sqlalchemy.orm import Session as DBSession

from app.config import settings, SUPPORTED_ROLES
from app.models import InterviewSession, Question, Answer, SessionSummary, Candidate
from app.rag.vector_store import query as vector_query
from app.services.query_builder import build_query, pick_topic
from app.services.question_generator import (
    generate_question,
    score_answer_strength,
    NEXT_DIFFICULTY,
)
from app.services.llm_client import get_client, is_llm_available


def _generate_and_store_question(
    db: DBSession, session: InterviewSession, difficulty: str
) -> Question:
    candidate: Candidate = session.candidate
    profile = candidate.extracted_profile or {}
    asked_topics = [q.topic for q in session.questions if q.topic]

    topic = pick_topic(profile, asked_topics)
    retrieval_query = build_query(session.role_label, profile, asked_topics)
    hits = vector_query(session.role_key, retrieval_query, top_k=settings.top_k)

    question_text = generate_question(
        role_label=session.role_label,
        topic=topic,
        context_chunks=hits,
        difficulty=difficulty,
        profile=profile,
        already_asked=asked_topics,
    )

    question = Question(
        session_id=session.id,
        order_index=len(session.questions),
        text=question_text,
        topic=topic,
        difficulty=difficulty,
        query_used=retrieval_query,
        source_chunks=[{"source": h["source"], "text": h["text"][:300]} for h in hits],
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def start_session(db: DBSession, candidate_id: str, role_key: str) -> InterviewSession:
    if role_key not in SUPPORTED_ROLES:
        raise ValueError(f"Unsupported role '{role_key}'")

    session = InterviewSession(
        candidate_id=candidate_id,
        role_key=role_key,
        role_label=SUPPORTED_ROLES[role_key],
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    _generate_and_store_question(db, session, difficulty="medium")
    db.refresh(session)
    return session


def submit_answer(db: DBSession, session: InterviewSession, answer_text: str):
    current_question = session.questions[session.current_question_index]
    strength = score_answer_strength(answer_text)

    answer = Answer(
        question_id=current_question.id, text=answer_text, strength_signal=strength
    )
    db.add(answer)

    session.current_question_index += 1

    is_last = session.current_question_index >= settings.questions_per_session
    if is_last:
        session.status = "completed"
        db.commit()
        _generate_summary(db, session)
        db.refresh(session)
        return session, None

    next_difficulty = NEXT_DIFFICULTY.get(strength, "medium")
    db.commit()
    db.refresh(session)
    next_question = _generate_and_store_question(db, session, next_difficulty)
    db.refresh(session)
    return session, next_question


def _llm_summary(session: InterviewSession) -> dict:
    client = get_client()
    transcript = []
    for q in session.questions:
        transcript.append(
            {
                "topic": q.topic,
                "difficulty": q.difficulty,
                "question": q.text,
                "answer": q.answer.text if q.answer else None,
            }
        )
    prompt = f"""You are summarizing a completed technical interview for a
{session.role_label} candidate. Here is the full transcript (JSON):
{json.dumps(transcript, indent=2)}

Return ONLY valid JSON (no markdown fences) with this shape:
{{
  "overall_summary": "2-4 sentence summary of overall performance",
  "strengths": ["short phrase", "..."],
  "growth_areas": ["short phrase", "..."],
  "topic_coverage": ["topics that were assessed"]
}}"""
    resp = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = "".join(b.text for b in resp.content if b.type == "text").strip()
    raw = re.sub(r"^```json|```$", "", raw.strip(), flags=re.MULTILINE).strip()
    return json.loads(raw)


def _fallback_summary(session: InterviewSession) -> dict:
    strengths, growth = [], []
    topics = []
    for q in session.questions:
        topics.append(q.topic)
        signal = q.answer.strength_signal if q.answer else None
        if signal in ("adequate", "strong"):
            strengths.append(q.topic)
        elif signal == "weak":
            growth.append(q.topic)
    return {
        "overall_summary": (
            f"Candidate answered {len(session.questions)} questions for the "
            f"{session.role_label} role, covering topics: {', '.join(dict.fromkeys(topics))}."
        ),
        "strengths": list(dict.fromkeys(strengths)) or ["N/A"],
        "growth_areas": list(dict.fromkeys(growth)) or ["N/A"],
        "topic_coverage": list(dict.fromkeys(topics)),
    }


def _generate_summary(db: DBSession, session: InterviewSession) -> SessionSummary:
    if is_llm_available():
        try:
            data = _llm_summary(session)
        except Exception:
            data = _fallback_summary(session)
    else:
        data = _fallback_summary(session)

    summary = SessionSummary(
        session_id=session.id,
        overall_summary=data["overall_summary"],
        strengths=data["strengths"],
        growth_areas=data["growth_areas"],
        topic_coverage=data["topic_coverage"],
    )
    db.add(summary)
    db.commit()
    return summary
