import uuid
from datetime import datetime, timezone

from sqlalchemy import String, CHAR, DATETIME, ForeignKey
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMBLOB, MEDIUMTEXT
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ChildProfile(Base):
    __tablename__ = "child_profiles"

    id: Mapped[str] = mapped_column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
    )
    user_id: Mapped[str] = mapped_column(
        CHAR(36), ForeignKey("users.id"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6), default=utcnow, nullable=False
    )


__all__ = ["ChildProfile"]
