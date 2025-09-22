from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from .tweet import Tweet
    from .user import User


class Like(Base):
    """
    Модель таблицы лайков твитов.
    """

    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id", ondelete="CASCADE"))

    user: Mapped["User"] = relationship(back_populates="likes")
    tweet: Mapped["Tweet"] = relationship(back_populates="likes")

    __table_args__ = (UniqueConstraint("user_id", "tweet_id", name="unique_user_like"),)

    @property
    def name(self) -> str:
        return self.user.name if self.user else ""
