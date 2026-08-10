from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class StartConversationRequest(BaseModel):
    channel: str = Field("chat", description="Communication channel: chat, whatsapp, app")


class ChatMessageRequest(BaseModel):
    conversation_id: Optional[str] = Field(None, description="Active conversation session ID")
    message: str = Field(..., min_length=1, max_length=2000, description="Customer message text")
    customer_profile: Optional[Dict[str, Any]] = Field(None, description="Live customer bank and account profile input")


class ChatMessageResponse(BaseModel):
    conversation_id: str
    user_message: str
    bot_response: str
    action_taken: str
    intent_id: str
    confidence: float
    sentiment_score: float
    detected_language: str
    latency_ms: float
    dialogue_state: Dict[str, Any]


class MessageRead(BaseModel):
    id: str
    conversation_id: str
    speaker: str
    encrypted_content: str
    classified_intent: Optional[str] = None
    intent_confidence: Optional[float] = None
    sentiment_score: Optional[float] = None
    created_at: Any

    model_config = ConfigDict(from_attributes=True)
