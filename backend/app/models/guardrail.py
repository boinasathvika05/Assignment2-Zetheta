from typing import Optional
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimeStampedModel


class GuardrailEvent(TimeStampedModel):
    """
    Guardrail Trigger Event logger recording activated safety rules and blocked adversarial attempts.
    """
    __tablename__ = "guardrail_events"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("messages.id", ondelete="SET NULL"), nullable=True)
    guardrail_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    attack_vector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action_taken: Mapped[str] = mapped_column(String(50), nullable=False)
    blocked_content_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="guardrail_events")
    message: Mapped[Optional["Message"]] = relationship("Message", back_populates="guardrail_events")
