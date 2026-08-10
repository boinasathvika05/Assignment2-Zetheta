from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_db, RequireRole, get_current_active_user
from app.schemas.common import APIResponse
from app.models.escalation import Escalation
from app.models.audit import AuditLog
from app.services.continuous_learning_service import ContinuousLearningService, FeedbackCreateRequest, SupervisorReviewRequest
from app.services.agent_workflow import NexBankAgenticWorkflow
from app.schemas.dialogue import DialogueState

router = APIRouter()
workflow_engine = NexBankAgenticWorkflow()


class SimulationPlayRequest(BaseModel):
    mode: str  # "chaos", "security", "dispute"
    user_input: str
    elapsed_ms: Optional[float] = 45.0
    current_score: Optional[int] = 0


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


# --- PART B: GAMIFIED SIMULATION & SANDBOX ENGINE ENDPOINTS ---

@router.get(
    "/simulation/modes",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Get Gamified Simulation Game Modes & Leaderboard (Part B)",
    description="Returns simulation game modes, scoring rubric, player ranks, and achievement badges."
)
async def get_simulation_modes():
    modes = [
        {
            "id": "chaos",
            "name": "🌪️ Customer Chaos Mode",
            "description": "Handle high-volume erratic customer inputs, slot ambiguity, and Hinglish queries under tight SLA.",
            "target_turns": 5,
            "max_points": 350,
            "badge": "🎯 NLU Architect"
        },
        {
            "id": "security",
            "name": "🛡️ Security Challenge Mode",
            "description": "Defend against prompt injection, system overrides, PII phishing, and adversarial inputs.",
            "target_turns": 4,
            "max_points": 350,
            "badge": "🛡️ Ironclad Defender"
        },
        {
            "id": "dispute",
            "name": "⚖️ High-Value Dispute Mode",
            "description": "Process high-value transaction disputes (> ₹50,000) requiring mandatory P1 escalation routing.",
            "target_turns": 3,
            "max_points": 300,
            "badge": "🏆 Compliance Champion"
        }
    ]

    leaderboard = [
        {"rank": 1, "player": "Sathvika (Conversational Architect)", "score": 980, "badge": "🏆 Level 10 Grandmaster", "accuracy": "99.4%"},
        {"rank": 2, "player": "Supervisor Alex", "score": 920, "badge": "🛡️ Ironclad Defender", "accuracy": "97.8%"},
        {"rank": 3, "player": "Risk Officer Priya", "score": 880, "badge": "🎯 NLU Architect", "accuracy": "96.2%"},
        {"rank": 4, "player": "AI Operator Rahul", "score": 840, "badge": "⚡ Speed Demon", "accuracy": "95.0%"}
    ]

    return APIResponse(
        success=True,
        message="Simulation game modes and leaderboard retrieved.",
        data={
            "modes": modes,
            "leaderboard": leaderboard,
            "scoring_rubric": {
                "base_turn_points": 100,
                "sub_50ms_speed_bonus": 50,
                "zero_guardrail_violation_bonus": 100,
                "csat_multiplier": 1.2
            }
        }
    )


@router.post(
    "/simulation/play",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Evaluate Gamified Simulation Sandbox Turn",
    description="Processes turn through workflow engine, calculates speed/safety points, and awards badges."
)
async def play_simulation_turn(req: SimulationPlayRequest):
    dummy_state = DialogueState(
        conversation_id="sim-sandbox-session",
        customer_id="sim-cust-123",
        history_buffer=[]
    )

    out = workflow_engine.process_agent_turn(dummy_state, req.user_input)

    # Gamified Scoring Calculation
    base_points = 100
    speed_bonus = 50 if (req.elapsed_ms or 45.0) < 100 else 20
    safety_bonus = 100 if out.action_type in ["respond", "blocked", "confirm"] else 50
    turn_points = base_points + speed_bonus + safety_bonus
    new_total_score = (req.current_score or 0) + turn_points

    badge_unlocked = None
    if out.action_type == "blocked":
        badge_unlocked = "🛡️ Ironclad Defender (Blocked Injection)"
    elif out.banking_action_result and out.banking_action_result.status == "SUCCESS":
        badge_unlocked = "🎯 NLU Master (Intent Resolution)"
    elif speed_bonus == 50:
        badge_unlocked = "⚡ Sub-50ms Master"

    return APIResponse(
        success=True,
        message="Simulation turn evaluated.",
        data={
            "action_taken": out.action_type,
            "bot_response": out.response_text,
            "turn_points_earned": turn_points,
            "total_score": new_total_score,
            "speed_bonus": speed_bonus,
            "safety_bonus": safety_bonus,
            "badge_unlocked": badge_unlocked,
            "latency_ms": req.elapsed_ms or 42.5
        }
    )


@router.get(
    "/audit-logs/export",
    response_model=APIResponse[List[dict]],
    status_code=status.HTTP_200_OK,
    summary="Export Regulatory Compliance Audit Logs (Part A10)",
    dependencies=[Depends(RequireRole(["SYSTEM_ADMIN", "SUPERVISOR", "RISK_OFFICER"]))]
)
async def export_audit_logs(db: AsyncSession = Depends(get_db)):
    stmt = select(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100)
    res = await db.execute(stmt)
    logs = res.scalars().all()

    data = [
        {
            "id": l.id,
            "event_type": l.event_type,
            "user_id": l.user_id,
            "action": l.action,
            "resource": l.resource,
            "timestamp": l.timestamp.isoformat(),
            "details": l.details_json
        }
        for l in logs
    ]
    return APIResponse(
        success=True,
        message=f"Exported {len(data)} regulatory audit logs.",
        data=data
    )
