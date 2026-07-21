from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models import Candidate, InterviewSession
from app.config import SUPPORTED_ROLES, settings
from app.schemas import (
    StartSessionRequest,
    StartSessionResponse,
    QuestionOut,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    SessionSummaryOut,
    QAItem,
)
from app.services import interview_service

router = APIRouter(prefix="/api/interview", tags=["interview"])


def _get_session_or_404(db: DBSession, session_id: str) -> InterviewSession:
    session = db.query(InterviewSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(404, "Session not found")
    return session


def _question_out(session: InterviewSession, question) -> QuestionOut:
    return QuestionOut(
        question_id=question.id,
        order_index=question.order_index,
        text=question.text,
        topic=question.topic,
        difficulty=question.difficulty,
        total_questions=settings.questions_per_session,
    )


@router.post("/start", response_model=StartSessionResponse)
def start_interview(payload: StartSessionRequest, db: DBSession = Depends(get_db)):
    candidate = db.query(Candidate).filter_by(id=payload.candidate_id).first()
    if not candidate:
        raise HTTPException(404, "Candidate not found -- upload a resume first")
    if payload.role_key not in SUPPORTED_ROLES:
        raise HTTPException(400, f"Unsupported role '{payload.role_key}'")

    session = interview_service.start_session(db, candidate.id, payload.role_key)
    first_question = session.questions[0]

    return StartSessionResponse(
        session_id=session.id,
        role_label=session.role_label,
        first_question=_question_out(session, first_question),
    )


@router.get("/{session_id}/current", response_model=QuestionOut)
def get_current_question(session_id: str, db: DBSession = Depends(get_db)):
    session = _get_session_or_404(db, session_id)
    if session.status == "completed":
        raise HTTPException(409, "Session already completed -- fetch /summary instead")
    question = session.questions[session.current_question_index]
    return _question_out(session, question)


@router.post("/{session_id}/answer", response_model=SubmitAnswerResponse)
def submit_answer(
    session_id: str, payload: SubmitAnswerRequest, db: DBSession = Depends(get_db)
):
    session = _get_session_or_404(db, session_id)
    if session.status == "completed":
        raise HTTPException(409, "Session already completed")
    if not payload.answer_text.strip():
        raise HTTPException(400, "Answer cannot be empty")

    session, next_question = interview_service.submit_answer(
        db, session, payload.answer_text
    )

    if next_question is None:
        return SubmitAnswerResponse(status="completed", next_question=None)

    return SubmitAnswerResponse(
        status="in_progress", next_question=_question_out(session, next_question)
    )


@router.get("/{session_id}/summary", response_model=SessionSummaryOut)
def get_summary(session_id: str, db: DBSession = Depends(get_db)):
    session = _get_session_or_404(db, session_id)
    if session.status != "completed" or not session.summary:
        raise HTTPException(409, "Session is not completed yet")

    transcript = [
        QAItem(
            order_index=q.order_index,
            question=q.text,
            topic=q.topic,
            difficulty=q.difficulty,
            answer=q.answer.text if q.answer else None,
        )
        for q in session.questions
    ]

    return SessionSummaryOut(
        session_id=session.id,
        role_label=session.role_label,
        status=session.status,
        overall_summary=session.summary.overall_summary,
        strengths=session.summary.strengths,
        growth_areas=session.summary.growth_areas,
        topic_coverage=session.summary.topic_coverage,
        transcript=transcript,
    )
