from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, CHAR, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMBLOB
from typing import Optional, List
from datetime import datetime


class Message(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "messages"

    conversation_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("conversations.id"), nullable=True, index=True)
    sender_user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False)
    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    sender_role: Mapped[str] = mapped_column(String(32), nullable=False)
    message_type: Mapped[str] = mapped_column(String(32), nullable=False, default="text")
    direction: Mapped[str] = mapped_column(String(32), nullable=False)
    content_enc: Mapped[bytes] = mapped_column(MEDIUMBLOB, nullable=False)
    level: Mapped[int] = mapped_column(TINYINT, nullable=False)
    source_message_id: Mapped[Optional[str]] = mapped_column(CHAR(36), nullable=True)
    source_message_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)


__all__ = ["Message"]
