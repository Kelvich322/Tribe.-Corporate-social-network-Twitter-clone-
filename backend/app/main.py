import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.api.handlers import universal_exception_handler
from app.api.routers.tweets import tweet_routers
from app.api.routers.users import user_routers
from app.db.database import engine, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Асинхронный контекстный менеджер жизненного цикла приложения FastAPI.
    Выполняет инициализацию при запуске приложения и очистку при завершении.
    """
    import app.models # type: ignore # noqa

    await init_db()
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.add_exception_handler(HTTPException, universal_exception_handler)
app.add_exception_handler(RequestValidationError, universal_exception_handler)
app.add_exception_handler(ValidationError, universal_exception_handler)
app.add_exception_handler(SQLAlchemyError, universal_exception_handler)
app.add_exception_handler(Exception, universal_exception_handler)

app.include_router(user_routers)
app.include_router(tweet_routers)
