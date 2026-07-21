"""
ORM models. Structured so the full lifecycle of an interview is
traceable end-to-end: Candidate -> InterviewSession -> Question -> Answer,
plus a SessionSummary that is generated once the session completes.
"""
import uuid
import datetime as dt

from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from app.database import Base


def gen_id() -> str:
    return uuid.uuid4().hex


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(String, primary_key=True, default=gen_id)
    resume_filename = Column(String, nullable=True)
    resume_text = Column(Text, nullable=True)
    # Structured extraction result: {"skills": [...], "technologies": [...], "domains": [...]}
    extracted_profile = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    sessions = relationship("InterviewSession", back_populates="candidate")


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String, primary_key=True, default=gen_id)
    candidate_id = Column(String, ForeignKey("candidates.id"))
    role_key = Column(String, nullable=False)          # e.g. "backend_engineer"
    role_label = Column(String, nullable=False)         # e.g. "Backend Engineer"
    status = Column(String, default="in_progress")      # in_progress | completed
    current_question_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    candidate = relationship("Candidate", back_populates="sessions")
    questions = relationship(
        "Question", back_populates="session", order_by="Question.order_index"
    )
    summary = relationship("SessionSummary", back_populates="session", uselist=False)


class Question(Base):
    __tablename__ = "questions"

    id = Column(String, primary_key=True, default=gen_id)
    session_id = Column(String, ForeignKey("interview_sessions.id"))
    order_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    topic = Column(String, nullable=True)
    difficulty = Column(String, default="medium")  # easy | medium | hard
    # Which retrieved chunks this question was grounded in -- keeps the
    # pipeline traceable (context -> question), per assignment section 7.5.
    source_chunks = Column(JSON, nullable=True)
    query_used = Column(Text, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    session = relationship("InterviewSession", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False)


class Answer(Base):
    __tablename__ = "answers"

    id = Column(String, primary_key=True, default=gen_id)
    question_id = Column(String, ForeignKey("questions.id"))
    text = Column(Text, nullable=False)
    # Cheap heuristic signal used to adapt difficulty of the next question
    strength_signal = Column(String, nullable=True)  # weak | adequate | strong
    submitted_at = Column(DateTime, default=dt.datetime.utcnow)

    question = relationship("Question", back_populates="answer")


class SessionSummary(Base):
    __tablename__ = "session_summaries"

    id = Column(String, primary_key=True, default=gen_id)
    session_id = Column(String, ForeignKey("interview_sessions.id"), unique=True)
    overall_summary = Column(Text, nullable=False)
    strengths = Column(JSON, nullable=True)
    growth_areas = Column(JSON, nullable=True)
    topic_coverage = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    session = relationship("InterviewSession", back_populates="summary")
