from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import settings
from app.db.database import Base

if TYPE_CHECKING:
    from .like import Like
    from .media import Media
    from .user import User


class Tweet(Base):
    """
    Модель таблицы твитов.
    """

    __tablename__ = "tweets"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(String(300))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="tweets")
    likes: Mapped[List["Like"]] = relationship(
        back_populates="tweet", cascade="all, delete-orphan"
    )

    medias: Mapped[List["Media"]] = relationship(
        back_populates="tweet", cascade="all, delete-orphan"
    )

    @property
    def attachments(self) -> list[str]:
        return [
            f"{settings.PUBLIC_BASE_URL}/{media.path.lstrip('/')}"
            for media in (self.medias or [])
        ]
