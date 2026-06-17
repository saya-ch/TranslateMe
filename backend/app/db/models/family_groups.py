from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import CHAR, ForeignKey


class FamilyGroup(Base, UUIDPK):
    __tablename__ = "family_groups"

    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)


__all__ = ["FamilyGroup"]
