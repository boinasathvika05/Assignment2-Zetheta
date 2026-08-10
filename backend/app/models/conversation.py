from typing import Optional, List
from sqlalchemy import String, Boolean, Float, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimeStampedModel
from app.core.enums import ResolutionStatus


class Conversation(TimeStampedModel):
    """
    Conversation entity tracking multi-turn customer session context.
    """
    __tablename__ = "conversations"

    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)
    channel: Mapped[str] = mapped_column(String(50), default="chat", nullable=False)
    primary_intent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    resolution_status: Mapped[ResolutionStatus] = mapped_column(
        SQLEnum(ResolutionStatus, name="resolution_status_enum"),
        default=ResolutionStatus.UNRESOLVED_ESCALATED,
        nullable=False,
        index=True
    )
    csat_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[str] = mapped_column(String(50), default="v1.0.0", nullable=False)
    turn_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    pii_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    customer: Mapped["CustomerProfile"] = relationship("CustomerProfile", back_populates="conversations")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    escalation: Mapped[Optional["Escalation"]] = relationship("Escalation", back_populates="conversation", uselist=False, cascade="all, delete-orphan")
    feedbacks: Mapped[List["Feedback"]] = relationship("Feedback", back_populates="conversation", cascade="all, delete-orphan")
    guardrail_events: Mapped[List["GuardrailEvent"]] = relationship("GuardrailEvent", back_populates="conversation", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="conversation", cascade="all, delete-orphan")
