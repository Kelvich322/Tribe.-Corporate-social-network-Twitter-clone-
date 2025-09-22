from pydantic import BaseModel


class LikeSchema(BaseModel):
    """
    Схема для отображения лайка
    """

    user_id: int
    name: str

    class Config:
        from_attributes = True


class LikeCreateSchema(BaseModel):
    """
    Схема для создания лайка
    """

    user_id: int
    tweet_id: int

    class Config:
        from_attributes = True
