from typing import Optional

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.media import Media


async def attach_media_to_tweet(db: AsyncSession, media_ids: Optional[list[int]], tweet_id: int):
    """
    Функция для обновления записи в таблице media.
    Привязывает к записи tweet_id, который при создании остаётся Null.
    """
    quary = (
        update(Media)
        .where(Media.id.in_(media_ids), Media.tweet_id.is_(None)) # type: ignore # noqa
        .values(tweet_id=tweet_id)
        .returning(Media.id)
    )
    try:
        await db.execute(quary)
        await db.commit()
    except SQLAlchemyError:
        return False


async def save_media_in_database(db: AsyncSession, path: str, tweet_id: Optional[int] = None):
    """
    Функция для создания записи в таблице media.
    """
    media: Media = Media(path=path, tweet_id=tweet_id)
    try:
        db.add(media)
        await db.commit()
        await db.refresh(media)
        return media
    except SQLAlchemyError:
        return None
