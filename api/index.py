import sys
import os

# Add parent and backend directories to sys.path for serverless environment
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend"))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Mark Vercel serverless environment flag
os.environ["VERCEL"] = "1"
os.environ["ENVIRONMENT"] = os.getenv("ENVIRONMENT", "production")

from app.main import app as fastapi_app

app = fastapi_app
handler = fastapi_app
