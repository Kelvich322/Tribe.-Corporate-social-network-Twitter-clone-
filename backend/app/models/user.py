from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from .followers import FollowerAssociation
    from .like import Like
    from .tweet import Tweet


class User(Base):
    """
    Модель таблицы пользователей.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    api_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    tweets: Mapped[List["Tweet"]] = relationship(back_populates="author")
    likes: Mapped[List["Like"]] = relationship(back_populates="user")

    followers: Mapped[List["FollowerAssociation"]] = relationship(
        foreign_keys="FollowerAssociation.following_id", back_populates="following_user"
    )

    following: Mapped[List["FollowerAssociation"]] = relationship(
        foreign_keys="FollowerAssociation.follower_id", back_populates="follower_user"
    )
