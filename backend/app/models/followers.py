from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User


class FollowerAssociation(Base):
    """
    Модель ассоциативной таблицы для подписок между пользователями.
    """

    __tablename__ = "follower_association"
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    following_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )

    follower_user: Mapped["User"] = relationship(
        foreign_keys=[follower_id], back_populates="following"
    )
    following_user: Mapped["User"] = relationship(
        foreign_keys=[following_id], back_populates="followers"
    )

    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="unique_followership"),
    )
