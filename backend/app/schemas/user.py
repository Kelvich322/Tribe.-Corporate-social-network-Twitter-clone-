from typing import List

from pydantic import BaseModel, Field


class UserBaseSchema(BaseModel):
    """
    Базовая схема пользователя
    """

    id: int
    name: str

    class Config:
        from_attributes = True
        populate_by_name = True


class UserInfoSchema(UserBaseSchema):
    """
    Схема для отображения пользователя.
    """

    followers: List[UserBaseSchema] = Field(alias="followers_users")
    following: List[UserBaseSchema] = Field(alias="following_users")


class UserSuccessResponse(BaseModel):
    """
    Схема для успешного ответа сервера после получения пользователя.
    """

    result: bool = Field(True)
    user: UserInfoSchema
