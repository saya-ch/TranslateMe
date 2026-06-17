from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMBLOB
from typing import Optional


class MemoryItem(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "memory_items"

    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    source_message_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("messages.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    raw_content_enc: Mapped[bytes] = mapped_column(MEDIUMBLOB, nullable=False)
    explainable_summary_enc: Mapped[Optional[bytes]] = mapped_column(MEDIUMBLOB, nullable=True)
    level: Mapped[int] = mapped_column(TINYINT, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    approved_by_child: Mapped[bool] = mapped_column(default=False)


__all__ = ["MemoryItem"]
