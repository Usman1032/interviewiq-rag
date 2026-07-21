"""Pydantic request/response models -- the API contract for the frontend."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class RoleOut(BaseModel):
    key: str
    label: str


class ResumeUploadResponse(BaseModel):
    candidate_id: str
    extracted_profile: Dict[str, Any]


class StartSessionRequest(BaseModel):
    candidate_id: str
    role_key: str


class QuestionOut(BaseModel):
    question_id: str
    order_index: int
    text: str
    topic: Optional[str] = None
    difficulty: str
    total_questions: int


class StartSessionResponse(BaseModel):
    session_id: str
    role_label: str
    first_question: QuestionOut


class SubmitAnswerRequest(BaseModel):
    answer_text: str


class SubmitAnswerResponse(BaseModel):
    status: str  # "in_progress" | "completed"
    next_question: Optional[QuestionOut] = None


class QAItem(BaseModel):
    order_index: int
    question: str
    topic: Optional[str]
    difficulty: str
    answer: Optional[str]


class SessionSummaryOut(BaseModel):
    session_id: str
    role_label: str
    status: str
    overall_summary: str
    strengths: List[str]
    growth_areas: List[str]
    topic_coverage: List[str]
    transcript: List[QAItem]
