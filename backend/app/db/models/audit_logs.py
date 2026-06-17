from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, CHAR, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT
from typing import Optional


class AuditLog(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=True, index=True)
    child_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(32), nullable=False)
    entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    level: Mapped[int] = mapped_column(TINYINT, nullable=False, default=0)
    changes_json: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)


__all__ = ["AuditLog"]
