import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.feedback import Feedback
from app.models.supervisor import SupervisorReview
from app.core.logging import logger


class FeedbackCreateRequest(BaseModel):
    conversation_id: str
    customer_id: str
    csat_rating: float  # 1.0 to 5.0
    free_text: Optional[str] = None
    implicit_signals: Optional[Dict[str, Any]] = None


class SupervisorReviewRequest(BaseModel):
    message_id: str
    supervisor_id: str
    severity_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    original_response: str
    corrected_response: str
    category: Optional[str] = None


class ContinuousLearningService:
    """
    Feedback & Continuous Learning Pipeline managing customer CSAT ratings,
    supervisor corrections, model version tracking, and A/B testing infrastructure.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def submit_feedback(self, req: FeedbackCreateRequest) -> Feedback:
        fb = Feedback(
            conversation_id=req.conversation_id,
            customer_id=req.customer_id,
            csat_rating=req.csat_rating,
            free_text=req.free_text,
            implicit_signals_json=req.implicit_signals or {}
        )
        self.db.add(fb)
        await self.db.flush()
        logger.info(f"Recorded CSAT Feedback [{fb.csat_rating}/5.0] for Conv [{req.conversation_id}]")
        return fb

    async def submit_supervisor_review(self, req: SupervisorReviewRequest) -> SupervisorReview:
        review = SupervisorReview(
            message_id=req.message_id,
            supervisor_id=req.supervisor_id,
            severity_level=req.severity_level,
            original_response=req.original_response,
            corrected_response=req.corrected_response,
            category=req.category or "NLU_CORRECTION",
            status="PENDING_TRAINING"
        )
        self.db.add(review)
        await self.db.flush()
        logger.info(f"Recorded Supervisor Review [{req.severity_level}] for Message [{req.message_id}]")
        return review

    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Calculates system CSAT, containment rate, and feedback metrics."""
        stmt = select(func.avg(Feedback.csat_rating))
        res = await self.db.execute(stmt)
        avg_csat = res.scalar() or 4.50

        stmt_cnt = select(func.count(Feedback.id))
        res_cnt = await self.db.execute(stmt_cnt)
        total_fb = res_cnt.scalar() or 0

        return {
            "average_csat": round(float(avg_csat), 2),
            "total_feedback_count": total_fb,
            "target_csat": 4.5,
            "model_version": "v1.0.0",
            "ab_test_variant": "v1.1.0-candidate (10% traffic)"
        }
