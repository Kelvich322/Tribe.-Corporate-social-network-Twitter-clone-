from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError


async def universal_exception_handler(request: Request, exc: Exception):
    """
    Универсальный обработчик исключений, возвращающий ошибки в формате:
    {
        "result": false,
        "error_type": str,
        "error_message": str
    }
    """

    if isinstance(exc, HTTPException):
        # Обработка стандартных HTTP исключений FastAPI
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "result": False,
                "error_type": f"HTTP_{exc.status_code}",
                "error_message": exc.detail,
            },
        )

    elif isinstance(exc, ValidationError):
        # Обработка ошибок валидации Pydantic
        errors = []
        for error in exc.errors():
            field = " -> ".join([str(loc) for loc in error["loc"]])
            errors.append(f"{field}: {error['msg']}")

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "result": False,
                "error_type": "VALIDATION_ERROR",
                "error_message": "Invalid request data",
            },
        )

    elif isinstance(exc, SQLAlchemyError):
        # Обработка ошибок базы данных
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "result": False,
                "error_type": "DATABASE_ERROR",
                "error_message": "Database operation failed",
            },
        )

    else:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "result": False,
                "error_type": "INTERNAL_SERVER_ERROR",
                "error_message": "Internal server error occurred",
            },
        )
