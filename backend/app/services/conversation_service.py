import json
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.enums import ResolutionStatus, AuthLevel
from app.core.logging import logger
from app.core.redis_client import get_redis_client
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.customer import CustomerProfile
from app.schemas.dialogue import DialogueState, TurnProcessResult
from app.services.agent_workflow import NexBankAgenticWorkflow, AgentWorkflowOutput
from app.services.escalation_service import EscalationRouterService


class ConversationService:
    """
    Service layer executing dialogue state tracking, conversation lifecycle,
    multi-session context carry-over, safety guardrails, human handoff, and agentic workflow orchestration.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.workflow = NexBankAgenticWorkflow()

    async def start_conversation(self, customer_id: str, channel: str = "chat") -> Conversation:
        """Initialize a new conversation session."""
        conv = Conversation(
            customer_id=customer_id,
            channel=channel,
            resolution_status=ResolutionStatus.UNRESOLVED_ESCALATED,
            turn_count=0,
            model_version="v1.0.0",
            pii_detected=False
        )
        self.db.add(conv)
        await self.db.flush()
        await self.db.refresh(conv)

        # Initialize Redis State
        state = DialogueState(
            conversation_id=conv.id,
            customer_id=customer_id
        )
        await self._save_state_to_redis(state)

        logger.info(f"Started new conversation session: {conv.id} for customer: {customer_id}")
        return conv

    async def get_dialogue_state(self, conversation_id: str) -> DialogueState:
        """Fetch dialogue state from Redis cache or fallback to Postgres DB."""
        try:
            client = await get_redis_client()
            if client:
                cached_json = await client.get(f"dialogue_state:{conversation_id}")
                if cached_json:
                    return DialogueState.model_validate_json(cached_json)
        except Exception as e:
            logger.warning(f"Redis state fetch fallback to DB for {conversation_id}: {str(e)}")

        # Fallback to DB
        stmt = select(Conversation).where(Conversation.id == conversation_id)
        res = await self.db.execute(stmt)
        conv = res.scalars().first()
        if not conv:
            raise ValueError(f"Conversation {conversation_id} not found.")

        state = DialogueState(
            conversation_id=conv.id,
            customer_id=conv.customer_id,
            current_intent=conv.primary_intent or "PRD-001"
        )
        return state

    async def _save_state_to_redis(self, state: DialogueState) -> None:
        try:
            client = await get_redis_client()
            if client:
                await client.set(
                    f"dialogue_state:{state.conversation_id}",
                    state.model_dump_json(),
                    ex=1800
                )
        except Exception as e:
            logger.warning(f"Redis state save skipped for {state.conversation_id}: {str(e)}")

    async def process_turn(
        self,
        conversation_id: str,
        user_text: str,
        customer_profile: Optional[Dict[str, Any]] = None
    ) -> TurnProcessResult:
        """
        Processes an incoming customer turn through Agentic Workflow:
        Runs Safety Guardrails -> NLU -> updates State -> checks Escalation -> executes Banking Action -> records Turn Message.
        """
        start_time = time.time()
        state = await self.get_dialogue_state(conversation_id)

        # Execute Agentic Workflow with live customer profile inputs
        workflow_out: AgentWorkflowOutput = self.workflow.process_agent_turn(
            state=state,
            user_text=user_text,
            customer_profile=customer_profile
        )
        updated_state = workflow_out.updated_state

        latency_ms = round((time.time() - start_time) * 1000, 2)

        # Record Escalation in DB if triggered
        if workflow_out.escalation_check and workflow_out.escalation_check.should_escalate:
            esc_router = EscalationRouterService()
            await esc_router.create_escalation_record(
                db=self.db,
                conversation_id=conversation_id,
                check=workflow_out.escalation_check,
                state=updated_state
            )

        # Record Messages in DB
        user_msg = Message(
            conversation_id=conversation_id,
            speaker="customer",
            encrypted_content=user_text,
            classified_intent=updated_state.current_intent,
            intent_confidence=updated_state.intent_confidence,
            sentiment_score=updated_state.sentiment_trajectory[-1] if updated_state.sentiment_trajectory else 0.0,
            latency_ms=latency_ms
        )
        self.db.add(user_msg)

        bot_msg = Message(
            conversation_id=conversation_id,
            speaker="agent",
            encrypted_content=workflow_out.response_text,
            classified_intent=updated_state.current_intent,
            intent_confidence=updated_state.intent_confidence,
            response_method=workflow_out.action_type,
            latency_ms=latency_ms
        )
        self.db.add(bot_msg)

        # Update Conversation Entity
        stmt = update(Conversation).where(Conversation.id == conversation_id).values(
            turn_count=Conversation.turn_count + 1,
            primary_intent=updated_state.current_intent
        )
        await self.db.execute(stmt)
        await self.db.flush()

        # Update Redis State Cache
        await self._save_state_to_redis(updated_state)

        return TurnProcessResult(
            conversation_id=conversation_id,
            user_message=user_text,
            bot_response=workflow_out.response_text,
            dialogue_state=updated_state,
            nlu_result={"intent_id": updated_state.current_intent, "confidence": updated_state.intent_confidence, "sentiment_language": {"sentiment_score": updated_state.sentiment_trajectory[-1] if updated_state.sentiment_trajectory else 0.0, "detected_language": "English"}},
            action_taken=workflow_out.action_type
        )

    async def get_history(self, conversation_id: str) -> List[Message]:
        """Fetch all messages for a conversation ordered chronologically."""
        stmt = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at.asc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
