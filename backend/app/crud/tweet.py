from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import FollowerAssociation, Like, Tweet


async def create_tweet(db: AsyncSession, data: dict):
    """
    Функция для создания записи в таблице tweets.
    """
    new_tweet = Tweet(**data)
    try:
        db.add(new_tweet)
        await db.commit()
        await db.refresh(new_tweet)
        return new_tweet
    except SQLAlchemyError:
        return None


async def get_feed_for_user(db: AsyncSession, user_id: int) -> list[Tweet]:
    """
    Функция для получения записей из таблицы tweets с сортировкой по количеству лайков.
    """
    following_subquery = (
        select(FollowerAssociation.following_id)
        .where(FollowerAssociation.follower_id == user_id)
        .scalar_subquery()
    )

    query = (
        select(Tweet, func.count(Like.id).label("likes_count"))
        .where(or_(Tweet.author_id.in_(following_subquery), Tweet.author_id == user_id))
        .outerjoin(Like, Like.tweet_id == Tweet.id)
        .options(
            selectinload(Tweet.author),
            selectinload(Tweet.likes).selectinload(Like.user),
            selectinload(Tweet.medias),
        )
        .group_by(Tweet.id)
        .order_by(func.count(Like.id).desc())
    )

    result = await db.execute(query)
    tweets = [row[0] for row in result.all()]
    return tweets


async def delete_tweet(db: AsyncSession, user_id: int, tweet_id: int) -> bool:
    """
    Функция для удаления записи из таблицы tweets.
    """
    query = select(Tweet).where(Tweet.id == tweet_id)
    result = await db.execute(query)
    tweet = result.scalar_one_or_none()
    if tweet is None:
        return False
    if tweet.author_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tweets",
        )
    try:
        await db.delete(tweet)
        await db.commit()
        return True
    except (SQLAlchemyError, HTTPException):
        await db.rollback()
        return False
