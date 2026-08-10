from typing import Optional, List
from sqlalchemy import String, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimeStampedModel


class Message(TimeStampedModel):
    """
    Message entity logging turn-level dialogue content, intent classification, and sentiment scores.
    """
    __tablename__ = "messages"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    speaker: Mapped[str] = mapped_column(String(20), nullable=False)  # "customer", "agent", "system"
    encrypted_content: Mapped[str] = mapped_column(Text, nullable=False)
    classified_intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    intent_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    entities_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    response_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # "template", "llm", "hybrid"
    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
    reviews: Mapped[List["SupervisorReview"]] = relationship("SupervisorReview", back_populates="message", cascade="all, delete-orphan")
    guardrail_events: Mapped[List["GuardrailEvent"]] = relationship("GuardrailEvent", back_populates="message", cascade="all, delete-orphan")
