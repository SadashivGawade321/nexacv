"""
Vercel serverless entry point for NexaCV FastAPI backend.
Adds the backend directory to sys.path so 'from app.xxx import' works.
"""
import sys
import os

_backend = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if _backend not in sys.path:
    sys.path.insert(0, _backend)

from app.main import app  # noqa: F401 — Vercel picks up `app`
