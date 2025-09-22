from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from .tweet import Tweet


class Media(Base):
    """
    Модель таблицы для медиа-файлов, прикреплённых к твитам.
    """

    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    path: Mapped[str] = mapped_column(String())
    tweet_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("tweets.id", ondelete="CASCADE"), nullable=True
    )

    tweet: Mapped["Tweet"] = relationship(back_populates="medias")
