from typing import Optional
from sqlalchemy import String, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimeStampedModel


class Feedback(TimeStampedModel):
    """
    Post-conversation CSAT rating & implicit feedback signal tracking entity.
    """
    __tablename__ = "feedbacks"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    csat_rating: Mapped[float] = mapped_column(Float, nullable=False)
    free_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    implicit_signals_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="feedbacks")
    customer: Mapped["CustomerProfile"] = relationship("CustomerProfile", back_populates="feedbacks")
