from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session as DBSession

from app.database import get_db
from app.models import Candidate
from app.schemas import ResumeUploadResponse
from app.services.resume_parser import extract_text_from_pdf_bytes, extract_profile

router = APIRouter(prefix="/api/resume", tags=["resume"])

ALLOWED_TYPES = {"application/pdf", "text/plain"}


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(file: UploadFile = File(...), db: DBSession = Depends(get_db)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, "Only PDF or plain text resumes are supported")

    raw = await file.read()
    if not raw:
        raise HTTPException(400, "Uploaded file is empty")

    if file.content_type == "application/pdf":
        resume_text = extract_text_from_pdf_bytes(raw)
    else:
        resume_text = raw.decode("utf-8", errors="ignore")

    if not resume_text.strip():
        raise HTTPException(422, "Could not extract any text from the resume")

    profile = extract_profile(resume_text)

    candidate = Candidate(
        resume_filename=file.filename,
        resume_text=resume_text,
        extracted_profile=profile,
    )
    db.add(candidate)
    db.commit()
    db.refresh(candidate)

    return ResumeUploadResponse(candidate_id=candidate.id, extracted_profile=profile)
