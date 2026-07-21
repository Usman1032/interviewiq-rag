"""
FastAPI application entrypoint. Wires up the DB, CORS, and routers.
Business logic lives in app/services, not here -- this file should stay
thin, per the "clear separation of responsibilities" expectation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import roles, resume, interview

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Candidate Screening System",
    description="RAG-powered, role-based technical interview backend",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(roles.router)
app.include_router(resume.router)
app.include_router(interview.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
