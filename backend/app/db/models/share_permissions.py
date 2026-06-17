from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import TINYINT
from typing import Optional


class SharePermission(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "share_permissions"

    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    source_message_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("messages.id"), nullable=True)
    source_draft_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("drafts.id"), nullable=True)
    granted_by_user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False)
    share_to_role: Mapped[str] = mapped_column(String(32), nullable=False)
    level: Mapped[int] = mapped_column(TINYINT, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)


__all__ = ["SharePermission"]
