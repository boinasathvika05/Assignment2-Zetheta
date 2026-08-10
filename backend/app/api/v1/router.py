from fastapi import APIRouter
from app.api.v1.endpoints import health, auth, chat, chat_ws, knowledge, governance

api_router = APIRouter()
api_router.include_router(health.router, tags=["System Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication & Security"])
api_router.include_router(chat.router, prefix="/chat", tags=["Conversation Engine & Chat"])
api_router.include_router(chat_ws.router, prefix="/chat", tags=["WebSocket Streaming Chat"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base & RAG Engine"])
api_router.include_router(governance.router, prefix="/governance", tags=["Safety, Escalation & Continuous Learning"])
