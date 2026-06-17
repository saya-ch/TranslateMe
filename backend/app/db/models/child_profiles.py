from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey


class ChildProfile(Base, UUIDPK):
    __tablename__ = "child_profiles"

    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)


__all__ = ["ChildProfile"]
