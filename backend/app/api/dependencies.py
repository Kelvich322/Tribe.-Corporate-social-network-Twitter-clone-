from typing import Annotated

from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.user import get_user_by_api_key
from app.db.database import async_session


async def get_db():
    """
    Генератор ассинхронных сессий БД.
    """
    async with async_session() as session:
        yield session


async def get_current_user(
    api_key: Annotated[str, Header(alias="Api-Key")],
    db: AsyncSession = Depends(get_db),
):
    """
    Функция возвращающая объект User из БД.
    Если объект не найден - выбрасывается HTTPException с 201 статус кодом.
    """
    user = await get_user_by_api_key(db=db, api_key=api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return user
