import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import CHAR, DATETIME


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class CreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(
        DATETIME(fsp=6),
        default=utcnow,
        nullable=False,
    )


class UpdatedAtMixin:
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DATETIME(fsp=6),
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
