from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, RequireRole, get_current_active_user
from app.schemas.common import APIResponse
from app.models.escalation import Escalation
from app.services.continuous_learning_service import ContinuousLearningService, FeedbackCreateRequest, SupervisorReviewRequest

router = APIRouter()


@router.post(
    "/feedback",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Submit Customer Feedback & CSAT Score",
    description="Records CSAT rating (1.0 to 5.0) and optional free text comments."
)
async def submit_feedback(req: FeedbackCreateRequest, db: AsyncSession = Depends(get_db)):
    cl_service = ContinuousLearningService(db)
    fb = await cl_service.submit_feedback(req)
    return APIResponse(
        success=True,
        message="Feedback recorded successfully.",
        data={"feedback_id": fb.id, "csat_rating": fb.csat_rating}
    )


@router.post(
    "/supervisor-review",
    response_model=APIResponse[dict],
    status_code=status.HTTP_201_CREATED,
    summary="Submit Supervisor Correction & Review",
    description="Submits human correction for model fine-tuning and learning pipeline.",
    dependencies=[Depends(RequireRole(["SUPERVISOR", "SYSTEM_ADMIN"]))]
)
async def submit_supervisor_review(req: SupervisorReviewRequest, db: AsyncSession = Depends(get_db)):
    cl_service = ContinuousLearningService(db)
    review = await cl_service.submit_supervisor_review(req)
    return APIResponse(
        success=True,
        message="Supervisor review submitted to learning queue.",
        data={"review_id": review.id, "status": review.status}
    )


@router.get(
    "/escalations",
    response_model=APIResponse[List[dict]],
    status_code=status.HTTP_200_OK,
    summary="List Open Escalations for Supervisor Dashboard",
    dependencies=[Depends(RequireRole(["SUPERVISOR", "SUPPORT_AGENT", "SYSTEM_ADMIN"]))]
)
async def list_escalations(db: AsyncSession = Depends(get_db)):
    stmt = select(Escalation).where(Escalation.status == "OPEN").order_by(Escalation.created_at.desc())
    res = await db.execute(stmt)
    escalations = res.scalars().all()
    
    data = [
        {
            "id": e.id,
            "conversation_id": e.conversation_id,
            "trigger_code": e.trigger_code,
            "priority": e.priority,
            "target_queue": e.target_queue,
            "sla_minutes": e.sla_minutes,
            "status": e.status,
            "created_at": e.created_at.isoformat()
        }
        for e in escalations
    ]
    return APIResponse(
        success=True,
        message=f"Retrieved {len(data)} open escalations.",
        data=data
    )


@router.get(
    "/metrics",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get System Governance Metrics & Model Version",
    description="Returns aggregate CSAT score, containment metrics, model version, and A/B test split."
)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    cl_service = ContinuousLearningService(db)
    metrics = await cl_service.get_metrics_summary()
    return APIResponse(
        success=True,
        message="Governance metrics retrieved.",
        data=metrics
    )
