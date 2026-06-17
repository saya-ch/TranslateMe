from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey


class Conversation(Base, UUIDPK):
    __tablename__ = "conversations"

    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    owner_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)


__all__ = ["Conversation"]
