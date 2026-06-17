from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey, DateTime
from typing import Optional
from datetime import datetime


class GroupMember(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "group_members"

    group_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("family_groups.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False, index=True)
    relation: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    joined_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


__all__ = ["GroupMember"]
