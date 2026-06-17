from app.db.base import Base, UUIDPK, CreatedAtMixin, UpdatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, CHAR, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMBLOB
from typing import Optional


class Draft(Base, UUIDPK, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "drafts"

    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    source_message_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("messages.id"), nullable=True)
    conversation_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("conversations.id"), nullable=True)
    title_enc: Mapped[bytes] = mapped_column(MEDIUMBLOB, nullable=False)
    body_enc: Mapped[bytes] = mapped_column(MEDIUMBLOB, nullable=False)
    suggestions_json: Mapped[Optional[str]] = mapped_column(String(4096), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="preview", index=True)
    to_role: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    level: Mapped[int] = mapped_column(TINYINT, nullable=False, default=3)


__all__ = ["Draft"]
