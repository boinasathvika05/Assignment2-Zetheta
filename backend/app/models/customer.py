from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimeStampedModel
from app.core.enums import AuthLevel


class CustomerProfile(TimeStampedModel):
    """
    NexBank Customer Profile storing banking segment, PEP status, and progressive auth level.
    """
    __tablename__ = "customer_profiles"

    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    pan_number_hashed: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    aadhaar_last4: Mapped[Optional[str]] = mapped_column(String(4), nullable=True)
    auth_level: Mapped[AuthLevel] = mapped_column(
        SQLEnum(AuthLevel, name="auth_level_enum"),
        default=AuthLevel.ANONYMOUS,
        nullable=False
    )
    segment: Mapped[str] = mapped_column(String(50), default="STANDARD", nullable=False)
    pep_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="customer_profile")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="customer", cascade="all, delete-orphan")
    feedbacks: Mapped[List["Feedback"]] = relationship("Feedback", back_populates="customer", cascade="all, delete-orphan")
