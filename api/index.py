import sys
import os

# Add parent and backend directories to sys.path for serverless environment
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))

# Mark Vercel serverless environment flag
os.environ["VERCEL"] = "1"

from app.main import app

# Export ASGI app & handler for Vercel serverless function entrypoint
handler = app
