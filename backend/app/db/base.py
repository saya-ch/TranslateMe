import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import CHAR


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utcnow,
        nullable=False,
    )


class UpdatedAtMixin:
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        default=utcnow,
        onupdate=utcnow,
        nullable=True,
    )


class UUIDPK:
    id: Mapped[str] = mapped_column(
        CHAR(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
    )


class CreatedAtIdPK(CreatedAtMixin, UUIDPK):
    pass


__all__ = ["Base", "CreatedAtMixin", "UpdatedAtMixin", "UUIDPK", "CreatedAtIdPK", "utcnow", "datetime"]
