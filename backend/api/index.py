"""
Vercel entry point for FastAPI backend.
This file is required for Vercel to properly route requests to the FastAPI app.
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and expose the FastAPI app
from api.main import app

# Vercel expects a callable named 'app' or 'handler'
__all__ = ['app']
