import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user, get_db
from app.crud.like import create_like, delete_like
from app.crud.media import attach_media_to_tweet, save_media_in_database
from app.crud.tweet import create_tweet, delete_tweet, get_feed_for_user
from app.models import User
from app.schemas.responses import ExceptionResponse, SuccessResponse
from app.schemas.tweet import (
    SuccessfullTweetGetResponse,
    SuccessMediaUploadResponse,
    SuccessTweetCreateResponse,
    TweetCreate,
    TweetSchema,
)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}

tweet_routers = APIRouter(prefix="/api", tags=["tweets"])


@tweet_routers.post(
    "/tweets",
    status_code=201,
    response_model=SuccessTweetCreateResponse,
    responses={
        201: {
            "model": SuccessTweetCreateResponse,
            "description": "Successful response with tweet ID",
        },
        400: {"model": ExceptionResponse, "description": "Bad request data"},
        422: {"model": ExceptionResponse, "description": "Validation error"},
        401: {"model": ExceptionResponse, "description": "Invalid API Key"},
    },
)
async def make_tweet(
    tweet_data: TweetCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Написать новый твит.
    """
    payload = {"content": tweet_data.content, "author_id": user.id}
    new_tweet = await create_tweet(db=db, data=payload)
    if tweet_data.tweet_media_ids:
        await attach_media_to_tweet(
            db=db, media_ids=tweet_data.tweet_media_ids, tweet_id=new_tweet.id
        )
    if new_tweet:
        return SuccessTweetCreateResponse(result=True, tweet_id=new_tweet.id)
    raise HTTPException(status_code=400, detail="Bad request data")


@tweet_routers.post(
    "/medias",
    status_code=201,
    responses={
        201: {
            "model": SuccessMediaUploadResponse,
            "description": "Successful upload media",
        },
        400: {"model": ExceptionResponse, "description": "Bad request data"},
        422: {"model": ExceptionResponse, "description": "Validation error"},
        401: {"model": ExceptionResponse, "description": "Invalid API Key"},
    },
)
async def upload_media(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Эндпоинт для загрузки изображений и прикрепления их к твиту.
    На прямую не используется и вызывается в момент отправки твита, если в форму были добавлены изображения.
    """
    filename = file.filename or "upload"
    file_extension = os.path.splitext(filename)[1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File format not allowed. Allowed formats: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    filename = os.path.basename(filename)
    user_dir = Path(f"/app/uploads/{user.name}")
    user_dir.mkdir(parents=True, exist_ok=True)
    path = user_dir / filename

    data = await file.read()
    with open(path, "wb") as f:
        f.write(data)
    await file.close()

    media = await save_media_in_database(db=db, path=str(path)[5:])
    if media:
        return SuccessMediaUploadResponse(result=True, media_id=media.id)
    raise HTTPException(status_code=400, detail="Bad request data")


@tweet_routers.get(
    "/tweets",
    response_model=SuccessfullTweetGetResponse,
    responses={
        200: {
            "model": SuccessfullTweetGetResponse,
            "description": "Successful response",
        },
        404: {
            "model": ExceptionResponse,
            "description": "Tweets not found for current user",
        },
        422: {"model": ExceptionResponse, "description": "Validation error"},
        401: {"model": ExceptionResponse, "description": "Invalid API Key"},
    },
)
async def get_tweets(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Получить ленту твитов для текущего аутентифицированного пользователя.
    """
    tweets = await get_feed_for_user(db=db, user_id=user.id)
    items = [
        TweetSchema.model_validate(tweet, from_attributes=True).model_dump()
        for tweet in tweets
    ]
    if tweets:
        return SuccessfullTweetGetResponse(result=True, tweets=items) # type: ignore # noqa
    raise HTTPException(status_code=404, detail="Tweets not found for current user")


@tweet_routers.delete(
    "/tweets/{id}",
    response_model=SuccessResponse,
    responses={
        200: {
            "model": SuccessfullTweetGetResponse,
            "description": "Successful response",
        },
        403: {
            "model": ExceptionResponse,
            "description": "You can only delete your own tweets",
        },
        422: {"model": ExceptionResponse, "description": "Validation error"},
        401: {"model": ExceptionResponse, "description": "Invalid API Key"},
    },
)
async def remove_tweet(
    id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Удалить твит.
    """
    result = await delete_tweet(db=db, user_id=user.id, tweet_id=id)
    if result:
        return SuccessResponse(result=result)
    raise HTTPException(status_code=403, detail="You can only delete your own tweets")


@tweet_routers.post(
    "/tweets/{id}/likes",
    response_model=SuccessResponse,
    status_code=201,
    responses={
        201: {
            "model": SuccessfullTweetGetResponse,
            "description": "Successful like tweet",
        },
        400: {"model": ExceptionResponse, "description": "Bad request data"},
        422: {"model": ExceptionResponse, "description": "Validation error"},
        401: {"model": ExceptionResponse, "description": "Invalid API Key"},
    },
)
async def like_tweet(
    id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Поставить лайк на твит.
    """
    new_like = await create_like(db=db, user_id=user.id, tweet_id=id)
    if new_like:
        return SuccessResponse(result=True)
    raise HTTPException(status_code=400, detail="Bad request data")


@tweet_routers.delete(
    "/tweets/{id}/likes",
    response_model=SuccessResponse,
    responses={
        200: {
            "model": SuccessfullTweetGetResponse,
            "description": "Successful like tweet",
        },
        400: {"model": ExceptionResponse, "description": "Bad request data"},
        422: {"model": ExceptionResponse, "description": "Validation error"},
        401: {"model": ExceptionResponse, "description": "Invalid API Key"},
    },
)
async def remove_like(
    id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """
    Убрать лайк с твита.
    """
    result = await delete_like(db=db, user_id=user.id, tweet_id=id)
    if result:
        return SuccessResponse(result=result)
    raise HTTPException(status_code=400, detail="Bad request data")
