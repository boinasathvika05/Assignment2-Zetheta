from typing import Optional
from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimeStampedModel
from app.core.enums import SeverityLevel


class SupervisorReview(TimeStampedModel):
    """
    Supervisor Review entity for model evaluation and continuous learning corrections.
    """
    __tablename__ = "supervisor_reviews"

    message_id: Mapped[str] = mapped_column(String(36), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    supervisor_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    severity_level: Mapped[SeverityLevel] = mapped_column(
        SQLEnum(SeverityLevel, name="severity_level_enum"),
        default=SeverityLevel.MINOR_STYLE_IMPROVEMENT,
        nullable=False
    )
    original_response: Mapped[str] = mapped_column(Text, nullable=False)
    corrected_response: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)

    # Relationships
    message: Mapped["Message"] = relationship("Message", back_populates="reviews")
    supervisor: Mapped["User"] = relationship("User", back_populates="reviews")
