from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey


class Conversation(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "conversations"

    child_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("child_profiles.id"), nullable=False, index=True)
    owner_user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(128), nullable=False, default="家庭对话")
    type: Mapped[str] = mapped_column(String(32), nullable=False, default="child_to_ai")


__all__ = ["Conversation"]
