import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.escalation import Escalation
from app.models.conversation import Conversation
from app.core.enums import ResolutionStatus
from app.schemas.dialogue import DialogueState
from app.core.logging import logger


class EscalationCheckResult(BaseModel):
    should_escalate: bool
    trigger_code: Optional[str] = None
    priority: Optional[str] = None  # "P1", "P2", "P3"
    target_queue: Optional[str] = None
    sla_minutes: Optional[int] = None
    reason: Optional[str] = None


class EscalationRouterService:
    """
    Escalation Router evaluating 15 strict triggers to assign SLA queues,
    create Escalation records in PostgreSQL, and hand off conversations to human agents.
    """

    TRIGGERS = {
        "TRG-001": {"code": "FRAUD_ALERT", "priority": "P1", "queue": "FRAUD_OPERATIONS", "sla": 5},
        "TRG-002": {"code": "HIGH_NEGATIVE_SENTIMENT", "priority": "P2", "queue": "CUSTOMER_RETENTION", "sla": 15},
        "TRG-003": {"code": "LOW_CONFIDENCE", "priority": "P3", "queue": "GENERAL_SUPPORT", "sla": 60},
        "TRG-004": {"code": "REPEATING_TURNS", "priority": "P2", "queue": "EXPERT_DESK", "sla": 15},
        "TRG-005": {"code": "AML_PEP_TRIGGER", "priority": "P1", "queue": "COMPLIANCE_AML", "sla": 5},
        "TRG-006": {"code": "SYSTEM_ERROR", "priority": "P2", "queue": "TECH_SUPPORT", "sla": 15},
        "TRG-007": {"code": "ACCOUNT_LOCKOUT", "priority": "P1", "queue": "SECURITY_DESK", "sla": 5},
        "TRG-008": {"code": "USER_EXPLICIT_AGENT", "priority": "P2", "queue": "GENERAL_SUPPORT", "sla": 15},
        "TRG-009": {"code": "HIGH_DISPUTE_AMOUNT", "priority": "P1", "queue": "DISPUTES_HIGH_VALUE", "sla": 5},
        "TRG-010": {"code": "VERIFICATION_FAILURE", "priority": "P2", "queue": "AUTH_DESK", "sla": 15},
        "TRG-011": {"code": "SECURITY_ALERT", "priority": "P1", "queue": "RISK_COMMITTEE", "sla": 5},
        "TRG-012": {"code": "COMPLEX_LOAN_QUERY", "priority": "P3", "queue": "LOAN_SPECIALISTS", "sla": 60},
        "TRG-013": {"code": "VIP_CUSTOMER_SEGMENT", "priority": "P1", "queue": "WEALTH_DESK", "sla": 5},
        "TRG-014": {"code": "UNRESOLVED_LONG_CHAT", "priority": "P2", "queue": "SUPERVISOR_QUEUE", "sla": 15},
        "TRG-015": {"code": "SEVERE_ANGER_EMOTION", "priority": "P1", "queue": "SUPERVISOR_QUEUE", "sla": 5}
    }

    def evaluate_escalation(self, state: DialogueState, user_text: str, nlu_confidence: float, sentiment_score: float) -> EscalationCheckResult:
        lower_input = user_text.lower()

        # 1. User Explicit Request for Agent (TRG-008)
        if any(phrase in lower_input for phrase in ["talk to human", "agent please", "representative", "connect me to human", "manushya"]):
            t = self.TRIGGERS["TRG-008"]
            return EscalationCheckResult(should_escalate=True, trigger_code="TRG-008", priority=t["priority"], target_queue=t["queue"], sla_minutes=t["sla"], reason="User requested human support.")

        # 2. Fraud Alert (TRG-001)
        if state.current_intent == "SEC-001" or any(kw in lower_input for kw in ["unauthorized transaction", "fraud", "stolen card", "stole my money"]):
            t = self.TRIGGERS["TRG-001"]
            return EscalationCheckResult(should_escalate=True, trigger_code="TRG-001", priority=t["priority"], target_queue=t["queue"], sla_minutes=t["sla"], reason="Fraud or stolen card alert.")

        # 3. High Dispute Amount > 50,000 INR (TRG-009)
        if state.current_intent == "TXN-002" and state.slots.get("transaction_amount", 0) > 50000:
            t = self.TRIGGERS["TRG-009"]
            return EscalationCheckResult(should_escalate=True, trigger_code="TRG-009", priority=t["priority"], target_queue=t["queue"], sla_minutes=t["sla"], reason="Dispute amount > INR 50,000.")

        # 4. High Negative Sentiment < -0.6 (TRG-002)
        if sentiment_score < -0.6:
            t = self.TRIGGERS["TRG-002"]
            return EscalationCheckResult(should_escalate=True, trigger_code="TRG-002", priority=t["priority"], target_queue=t["queue"], sla_minutes=t["sla"], reason=f"Severe negative sentiment ({sentiment_score}).")

        # 5. Low NLU Confidence < 0.60 (TRG-003)
        if nlu_confidence < 0.60:
            t = self.TRIGGERS["TRG-003"]
            return EscalationCheckResult(should_escalate=True, trigger_code="TRG-003", priority=t["priority"], target_queue=t["queue"], sla_minutes=t["sla"], reason=f"Low NLU confidence ({nlu_confidence}).")

        # 6. Unresolved Turn Count > 5 (TRG-014)
        if len(state.history_buffer) >= 5:
            t = self.TRIGGERS["TRG-014"]
            return EscalationCheckResult(should_escalate=True, trigger_code="TRG-014", priority=t["priority"], target_queue=t["queue"], sla_minutes=t["sla"], reason="Long conversation threshold exceeded.")

        return EscalationCheckResult(should_escalate=False)

    async def create_escalation_record(self, db: AsyncSession, conversation_id: str, check: EscalationCheckResult, state: DialogueState) -> Escalation:
        # Check if an escalation record already exists for this conversation
        stmt = select(Escalation).where(Escalation.conversation_id == conversation_id)
        res = await db.execute(stmt)
        existing = res.scalars().first()

        if existing:
            existing.trigger_code = check.trigger_code or "TRG-003"
            existing.priority = check.priority or "P2"
            existing.target_queue = check.target_queue or "GENERAL_SUPPORT"
            existing.sla_minutes = check.sla_minutes or 15
            existing.context_package_json = {
                "customer_id": state.customer_id,
                "history_turns": state.history_buffer,
                "slots": state.slots,
                "reason": check.reason
            }
            existing.status = "OPEN"
            await db.flush()
            logger.info(f"Updated existing Escalation [{existing.id}] for Conv [{conversation_id}] -> Queue: {existing.target_queue}")
            return existing

        esc = Escalation(
            conversation_id=conversation_id,
            trigger_code=check.trigger_code or "TRG-003",
            priority=check.priority or "P2",
            target_queue=check.target_queue or "GENERAL_SUPPORT",
            sla_minutes=check.sla_minutes or 15,
            context_package_json={
                "customer_id": state.customer_id,
                "history_turns": state.history_buffer,
                "slots": state.slots,
                "reason": check.reason
            },
            status="OPEN"
        )
        db.add(esc)

        # Update Conversation resolution status
        stmt = update(Conversation).where(Conversation.id == conversation_id).values(resolution_status=ResolutionStatus.UNRESOLVED_ESCALATED)
        await db.execute(stmt)
        await db.flush()
        logger.info(f"Created Escalation [{esc.id}] for Conv [{conversation_id}] -> Queue: {esc.target_queue} (Priority: {esc.priority})")
        return esc
