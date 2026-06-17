from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMBLOB
from typing import Optional
from datetime import datetime


class InboxMessage(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "inbox_messages"

    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    share_id: Mapped[Optional[str]] = mapped_column(CHAR(36), ForeignKey("share_permissions.id"), nullable=True)
    from_role: Mapped[str] = mapped_column(String(32), nullable=False)
    to_role: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    title_enc: Mapped[bytes] = mapped_column(MEDIUMBLOB, nullable=False)
    body_enc: Mapped[bytes] = mapped_column(MEDIUMBLOB, nullable=False)
    level: Mapped[int] = mapped_column(TINYINT, nullable=False)
    read: Mapped[bool] = mapped_column(default=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="delivered", index=True)
    permission_id: Mapped[Optional[str]] = mapped_column(CHAR(36), nullable=True)


__all__ = ["InboxMessage"]
