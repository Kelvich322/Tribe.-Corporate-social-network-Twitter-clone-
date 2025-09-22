from sqlalchemy import delete, insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FollowerAssociation


async def follow_user(db: AsyncSession, following_id: int, follower_id: int):
    """
    Функция для создания записи в таблице follower_association.
    """
    query = insert(FollowerAssociation).values(
        follower_id=follower_id, following_id=following_id
    )
    try:
        await db.execute(query)
        await db.commit()
        return True
    except SQLAlchemyError:
        await db.rollback()
        return False


async def delete_follow_association(
    db: AsyncSession, following_id: int, follower_id: int
):
    """
    Функция для удаления записи в таблице follower_association.
    """
    query = delete(FollowerAssociation).where(
        FollowerAssociation.follower_id == follower_id,
        FollowerAssociation.following_id == following_id,
    )
    try:
        await db.execute(query)
        await db.commit()
        return True
    except SQLAlchemyError:
        return False
