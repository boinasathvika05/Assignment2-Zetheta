from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import TimeStampedModel
from app.core.enums import UserRole


class User(TimeStampedModel):
    """
    Core User entity supporting RBAC roles across Customer, Support Agent, Supervisor, Risk Officer, and System Admin.
    """
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role_enum"),
        default=UserRole.CUSTOMER,
        nullable=False,
        index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    customer_profile: Mapped[Optional["CustomerProfile"]] = relationship("CustomerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    sessions: Mapped[List["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    assigned_escalations: Mapped[List["Escalation"]] = relationship("Escalation", back_populates="assigned_agent", foreign_keys="[Escalation.assigned_agent_id]")
    reviews: Mapped[List["SupervisorReview"]] = relationship("SupervisorReview", back_populates="supervisor", foreign_keys="[SupervisorReview.supervisor_id]")
