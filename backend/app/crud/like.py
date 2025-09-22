from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Like


async def create_like(db: AsyncSession, user_id: int, tweet_id: int):
    """
    Функция для создания записи в таблице likes.
    """
    new_like = Like(user_id=user_id, tweet_id=tweet_id)
    try:
        db.add(new_like)
        await db.commit()
        await db.refresh(new_like)
        return new_like
    except SQLAlchemyError:
        return None


async def delete_like(db: AsyncSession, user_id: int, tweet_id: int):
    """
    Функция для удаления записи в таблице likes.
    """
    query = delete(Like).where(Like.tweet_id == tweet_id, Like.user_id == user_id)
    try:
        await db.execute(query)
        await db.commit()
        return True
    except SQLAlchemyError:
        return False
