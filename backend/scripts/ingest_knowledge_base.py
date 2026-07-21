"""
Run this once before starting the server (and again any time you add new
source docs) to (re)build the vector store:

    python scripts/ingest_knowledge_base.py

Add real corpus PDFs under app/knowledge_base/<role_key>/ first -- see
README for the recommended sources per role.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import SUPPORTED_ROLES
from app.rag.ingest import ingest_all_roles

if __name__ == "__main__":
    results = ingest_all_roles(list(SUPPORTED_ROLES.keys()))
    for role_key, count in results.items():
        print(f"[{role_key}] ingested {count} chunks")
