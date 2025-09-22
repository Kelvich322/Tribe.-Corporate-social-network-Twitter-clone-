from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Класс Settings - наследник BaseSettings из pydantic_settings.
    Подтягивает переменные окружения из файла .env,
    если они не указаны, то ставит значения по умолчанию.

    Attributes:
        DATABASE_URL (str): URL для подключения к PostgreSQL базе данных
        PUBLIC_BASE_URL (str): Базовый URL фронтенда
    """

    DATABASE_URL: str = "postgresql+asyncpg://user:password@db:5432/tribe"
    PUBLIC_BASE_URL: str = "http://localhost"

    class Config:
        env_file = ".env"


settings = Settings()
