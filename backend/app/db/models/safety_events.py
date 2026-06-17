from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey, DateTime
from typing import Optional
from datetime import datetime


class SafetyEvent(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "safety_events"

    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    source_message_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("messages.id"), nullable=True)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    patterns: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending", index=True)
    resolved_by_user_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    safety_resources_json: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)


__all__ = ["SafetyEvent"]
