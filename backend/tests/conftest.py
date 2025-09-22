from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.api.dependencies import get_db
from app.db.database import Base
from app.main import app
from app.models.user import User


@pytest.fixture(scope="session")
def postgres_container():
    """Генератор, который запускает PostgreSQL в Docker контейнере."""
    with PostgresContainer(image="postgres:15", driver="asyncpg") as container:
        container.start()
        yield container


@pytest.fixture(scope="session")
def test_database_url(postgres_container):
    """Возвращает URL для подключения к тестовой БД."""
    url = postgres_container.get_connection_url()
    print(f"\n\n{url}\n\n")
    return url


@pytest_asyncio.fixture(scope="function")
async def engine(test_database_url):
    """Создаёт и возвращает асинхронный engine базы данных для тестов."""
    import app.models

    engine = create_async_engine(test_database_url, future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def session_maker(engine):
    """Создаёт фабрику асинхронных сессий для тестовой БД."""
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture
async def db_session(session_maker):
    """Предоставляет асинхронную сессию базы данных для теста."""
    async with session_maker() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def override_db(db_session):
    """Переопределяет зависимость get_db для тестов."""

    async def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client():
    """Создаёт ассинхронный тестовый клиет для HTTP-запросов."""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client


@pytest_asyncio.fixture
async def test_user(db_session):
    """Создаёт и возвращает тестового пользователя в базе данных."""
    user = User(name="Test", api_key=f"test-{uuid4()}")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_another_user(db_session):
    """Создаёт и возвращает тестового пользователя в базе данных."""
    user = User(name="Test", api_key=f"test-{uuid4()}")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user
