"""
Vercel entry point.

Vercel runs every request through this one Python function; vercel.json
rewrites all paths here, and Flask routes them as usual (static files included).
"""
import os
import sys

# Make the project root importable (wsgi.py, app/, config/)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from wsgi import app  # noqa: E402,F401
