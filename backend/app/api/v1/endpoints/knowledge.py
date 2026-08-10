from typing import List, Optional
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_active_user
from app.schemas.common import APIResponse
from app.services.knowledge_service import KnowledgeService
from app.services.rag.hybrid_retriever import RAGSearchResult

router = APIRouter()


class SearchQueryRequest(BaseModel):
    query: str
    top_k: int = 5
    category: Optional[str] = None


@router.post(
    "/search",
    response_model=APIResponse[List[RAGSearchResult]],
    status_code=status.HTTP_200_OK,
    summary="Execute Hybrid RAG Knowledge Search",
    description="Combines Dense Vector Retrieval (0.6) and Sparse BM25 (0.4) with Cross-Encoder Re-Ranking under 200ms."
)
async def search_knowledge(req: SearchQueryRequest, db: AsyncSession = Depends(get_db)):
    kb_service = KnowledgeService(db)
    results = await kb_service.search(query=req.query, top_k=req.top_k, category=req.category)
    return APIResponse(
        success=True,
        message=f"Retrieved {len(results)} relevant knowledge items.",
        data=results
    )


@router.post(
    "/seed",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Seed 50+ Production Knowledge Base Entries",
    description="Populates PostgreSQL database and ChromaDB vector index with 50+ banking product, policy, and regulatory guidelines."
)
async def seed_knowledge(db: AsyncSession = Depends(get_db)):
    kb_service = KnowledgeService(db)
    count = await kb_service.seed_knowledge_base()
    return APIResponse(
        success=True,
        message=f"Seeded {count} new knowledge base entries." if count > 0 else "Knowledge base already seeded.",
        data={"seeded_count": count}
    )
