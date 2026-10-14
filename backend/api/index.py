"""Vercel entry point for the FastAPI application."""

import sys
from pathlib import Path

# Ensure repository-root imports work when Vercel loads this file directly.
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
if str(REPOSITORY_ROOT) not in sys.path:
    sys.path.insert(0, str(REPOSITORY_ROOT))

from backend.api.main import app  # noqa: E402

__all__ = ["app"]
