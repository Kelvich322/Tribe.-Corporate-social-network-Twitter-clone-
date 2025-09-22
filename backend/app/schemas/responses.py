from pydantic import BaseModel


class ExceptionResponse(BaseModel):
    """
    Схема для ответа сервера в случае ошибки.
    """

    result: bool = False
    error_type: str
    error_message: str


class SuccessResponse(BaseModel):
    """
    Схема успешного ответа сервера.
    """

    result: bool
