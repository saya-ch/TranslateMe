from app.db.base import Base, UUIDPK, CreatedAtMixin
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, CHAR, ForeignKey


class User(Base, UUIDPK, CreatedAtMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(64), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)


__all__ = ["User"]
