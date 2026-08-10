from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimeStampedModel
from app.core.enums import EscalationPriority


class Escalation(TimeStampedModel):
    """
    Human-in-the-Loop Escalation entity capturing 15 trigger conditions and SLA details.
    """
    __tablename__ = "escalations"

    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    trigger_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)  # e.g., ESC-001
    priority: Mapped[EscalationPriority] = mapped_column(
        SQLEnum(EscalationPriority, name="escalation_priority_enum"),
        default=EscalationPriority.P2,
        nullable=False,
        index=True
    )
    target_queue: Mapped[str] = mapped_column(String(100), nullable=False)
    sla_minutes: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    context_package_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="QUEUED", nullable=False, index=True)
    assigned_agent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="escalation")
    assigned_agent: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_escalations")
