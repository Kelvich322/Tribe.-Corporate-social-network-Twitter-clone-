from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.likes import LikeSchema
from app.schemas.user import UserBaseSchema


class TweetCreate(BaseModel):
    """
    Схема для создания твита.
    """

    content: str = Field(alias="tweet_data")
    tweet_media_ids: Optional[List[int]] = []

    class Config:
        from_attributes = True
        populate_by_name = True


class TweetSchema(BaseModel):
    """
    Схема для отображения твита.
    """

    id: int
    content: str
    author: UserBaseSchema
    likes: List[LikeSchema] = Field(default_factory=list)
    attachments: List[str] = Field(default_factory=list)

    class Config:
        from_attributes = True


class SuccessTweetCreateResponse(BaseModel):
    """
    Схема для успешного ответа сервера после создания твита.
    """

    result: bool
    tweet_id: int


class SuccessMediaUploadResponse(BaseModel):
    """
    Схема для успешного ответа сервера после загрузки изображения к твиту.
    """

    result: bool
    media_id: int


class SuccessfullTweetGetResponse(BaseModel):
    """
    Схема для успешного ответа сервера после ленты твитов.
    """

    result: bool
    tweets: List[TweetSchema]
