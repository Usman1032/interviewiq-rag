# AI Candidate Screening System

A role-based technical interview simulator. A candidate uploads a resume and
picks a role; the system extracts their profile, retrieves grounded context
from a role-specific knowledge base via RAG, generates interview questions
live, runs an adaptive Q&A session, and produces a structured summary.

Built for the PG-AGI AI/ML & Backend Intern assignment.

## Architecture

```
frontend/  Next.js (pages router) — resume upload, role select, chat-style
           interview, summary view. Talks to the backend over REST.

backend/   FastAPI service
  app/routers/     HTTP layer only — request/response, status codes
  app/services/    Business logic (resume parsing, query building,
                    question generation, interview orchestration)
  app/rag/         Ingestion, chunking, embeddings, vector store
  app/models.py    SQLAlchemy models (SQLite by default)
  app/knowledge_base/<role>/  source documents per role (sample docs
                    included; swap in the full textbooks from the
                    assignment brief for production use)
```
## Demo Video

[Video demo] = https://drive.google.com/file/d/1WXbFnHGZ6qJ7kPkAeRsmmU3L1IOn0uCR/view?usp=sharing

### Data flow

```
Resume upload → text extraction → keyword + (optional) LLM profile extraction
      → Candidate stored

Start interview → for each question:
   pick an unexplored topic from the resume profile
   → build a retrieval query ("<role> interview concepts related to <topic>")
   → query the role's Chroma collection (embeddings via sentence-transformers)
   → generate a question grounded in the retrieved chunks (Claude, with a
     deterministic template fallback if no API key is set)
   → store question + which chunks it was grounded in (traceability)

Submit answer → store answer → cheap heuristic scores answer strength
   (word-count based) → next question's difficulty adapts to that signal
   → after N questions, session is marked completed and a summary is
     generated (LLM-assisted, with a deterministic fallback) from the
     full transcript
```

### Key design decisions

- **Local embeddings, API-based generation.** Retrieval (embeddings +
  vector search) runs entirely locally via `sentence-transformers` +
  Chroma — no API key required, fast, free, deterministic. Only question
  and summary *generation* call the Anthropic API. If `ANTHROPIC_API_KEY`
  is unset, both fall back to deterministic template/heuristic logic so
  the full pipeline still runs end-to-end for local grading — you just
  get less varied questions.
- **One vector collection per role**, not one collection with a role
  filter. Keeps retrieval scoped, ingestion of one role independent of
  the others, and avoids leaking Backend Engineer content into an AI/ML
  interview.
- **Fixed-size chunking with overlap** (default 800 chars / 120 overlap,
  configurable via env vars). A simple, dependency-light strategy that
  still preserves context across chunk boundaries — appropriate given
  the 48-hour scope; a semantic/recursive chunker would be the next
  upgrade for longer-form textbook PDFs.
- **Traceable pipeline.** Every stored `Question` row records the
  retrieval query used and the source chunks it was grounded in, so you
  can inspect *why* a question was asked, per the assignment's "ensure
  traceability" requirement.
- **Difficulty adapts on a cheap, explainable signal** (answer length as
  a proxy for depth) rather than a black-box scorer, so the adaptation
  logic is easy to audit and swap out.
- **Graceful degradation everywhere an LLM call is made** — resume
  refinement, question generation, and summary generation all wrap the
  Claude call in a try/except with a deterministic fallback, so a flaky
  network or missing API key never breaks the flow.

## Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- An Anthropic API key (optional — enables higher-quality question/summary
  generation; the system runs without one using fallback logic)

### Backend

```bash
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
   # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
python scripts/ingest_knowledge_base.py

cp .env.example .env
# edit .env and add ANTHROPIC_API_KEY if you have one

# Build the vector store from the sample knowledge base
python scripts/ingest_knowledge_base.py

The API is now live at `http://localhost:8000` (interactive docs at
`/docs`).

To use the full textbooks from the assignment brief instead of the
included samples: drop the PDFs into
`app/knowledge_base/<role_key>/` (roles: `backend_engineer`,
`ai_ml_engineer`, `data_scientist`) and re-run the ingestion script.

### Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local   # points at http://localhost:8000 by default
npm run dev
```

Visit `http://localhost:3000`.

## API overview

| Method | Path                              | Purpose                              |
|--------|------------------------------------|---------------------------------------|
| GET    | `/api/roles`                       | List supported roles                  |
| POST   | `/api/resume/upload`               | Upload resume, get back extracted profile |
| POST   | `/api/interview/start`             | Start a session, get the first question |
| GET    | `/api/interview/{id}/current`      | Fetch the current pending question    |
| POST   | `/api/interview/{id}/answer`       | Submit an answer, get the next question or completion |
| GET    | `/api/interview/{id}/summary`      | Structured summary + full transcript  |

## Known limitations / next steps

- Sample knowledge base docs are short hand-written summaries, not the
  full textbooks — swap in the real PDFs for a production-quality demo.
- Difficulty adaptation uses answer length as a proxy signal; a
  correctness-aware scorer (comparing the answer against the retrieved
  context) would be a stronger next iteration.
- No auth layer — out of scope for this assignment, but a real deployment
  would need it before storing candidate resumes.
- SQLite is used for simplicity; `DATABASE_URL` can be pointed at Postgres
  with no code changes.
