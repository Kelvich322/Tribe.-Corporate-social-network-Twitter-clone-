from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import FollowerAssociation, User


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """
    Функция для получения записи из таблицы users по id.
    """
    query = (
        select(User)
        .where(User.id == user_id)
        .options(
            joinedload(User.followers).joinedload(FollowerAssociation.follower_user),
            joinedload(User.following).joinedload(FollowerAssociation.following_user),
        )
    )
    result = await db.execute(query)
    user = result.unique().scalar_one_or_none()
    if user:
        user.followers_users = [assoc.follower_user for assoc in user.followers]
        user.following_users = [assoc.following_user for assoc in user.following]

    return user


async def get_user_by_api_key(db: AsyncSession, api_key: str) -> User | None:
    """
    Функция для получения записи из таблицы users по api_key.
    """
    query = (
        select(User)
        .where(User.api_key == api_key)
        .options(
            joinedload(User.followers).joinedload(FollowerAssociation.follower_user),
            joinedload(User.following).joinedload(FollowerAssociation.following_user),
        )
    )
    result = await db.execute(query)
    user = result.unique().scalar_one_or_none()
    if user:
        user.followers_users = [assoc.follower_user for assoc in user.followers]
        user.following_users = [assoc.following_user for assoc in user.following]

    return user
