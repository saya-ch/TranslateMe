from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import TINYINT
from typing import Optional
from datetime import datetime


class Consent(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "consents"

    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    actor_user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False)
    scope: Mapped[str] = mapped_column(String(128), nullable=False)
    purpose: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    level: Mapped[int] = mapped_column(TINYINT, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active", index=True)
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


__all__ = ["Consent"]
