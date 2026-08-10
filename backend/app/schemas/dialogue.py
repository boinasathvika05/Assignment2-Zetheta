from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class DialogueState(BaseModel):
    """
    Dialogue State Object tracking active conversation context across turns.
    """
    conversation_id: str
    customer_id: str
    current_intent: str = "PRD-001"
    intent_confidence: float = 0.90
    alternative_intents: List[Dict[str, Any]] = []
    slots: Dict[str, Any] = {}
    history_buffer: List[Dict[str, Any]] = []  # Configurable depth (last 20 turns)
    sentiment_trajectory: List[float] = [0.0]
    auth_level: str = "ANONYMOUS"
    guardrail_state: Dict[str, bool] = {
        "financial_advice_prohibition": True,
        "pii_masking": True,
        "adversarial_scanner": True
    }
    escalation_proximity: float = 0.0
    multi_session_context: Dict[str, Any] = {}


class TurnProcessResult(BaseModel):
    conversation_id: str
    user_message: str
    bot_response: str
    dialogue_state: DialogueState
    nlu_result: Dict[str, Any]
    action_taken: str  # "respond", "clarify", "confirm", "escalate"
