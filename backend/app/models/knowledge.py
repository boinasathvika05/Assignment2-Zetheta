from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import TimeStampedModel


class KnowledgeEntry(TimeStampedModel):
    """
    Knowledge Base entity supporting structured key-value, semi-structured JSON, and unstructured passages.
    """
    __tablename__ = "knowledge_entries"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    format_type: Mapped[str] = mapped_column(String(50), default="unstructured", nullable=False)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    regulatory_tags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    ttl_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
