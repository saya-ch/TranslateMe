from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey


class FamilyGroup(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "family_groups"

    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, default="家庭组")


__all__ = ["FamilyGroup"]
