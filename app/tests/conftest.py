import pytest
import pytest_asyncio
from faker import Faker
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.base import Base
from app.core.config import settings
from app.core.database import get_db
from app.main import app
from app.models.post import Post  # noqa: F401
from app.models.post_like import PostLike  # noqa: F401
# Keep all models imported so Base.metadata is fully populated
from app.models.user import User  # noqa: F401
# Pull fixture modules into conftest scope so pytest discovers them
from app.tests.fixtures.auth_fixtures import (  # noqa: F401
    authenticated_user,
    auth_headers,
    user,
)
from app.tests.fixtures.post_fixtures import post  # noqa: F401
from app.tests.fixtures.user_fixtures import second_user  # noqa: F401

# ---------------------------------------------------------------------------
# Test database URL — uses TEST_DB from .env
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}"
    f"/{settings.TEST_DB}"
)

# ---------------------------------------------------------------------------
# Single engine for the whole test session
# ---------------------------------------------------------------------------
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
)

TestAsyncSessionFactory = async_sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
    class_=AsyncSession,
)


# ---------------------------------------------------------------------------
# Create all tables once; drop them at the very end
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # clean slate
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


# ---------------------------------------------------------------------------
# Per-test isolation via SAVEPOINT (nested transaction).
#
# Repositories call session.commit() inside them, which would normally flush
# to the DB permanently.  By wrapping the whole test in a SAVEPOINT we can
# roll back to the savepoint at the end regardless of any inner commits.
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def db_session():
    async with test_engine.connect() as conn:
        await conn.begin()  # outer real transaction
        nested = await conn.begin_nested()  # SAVEPOINT

        session = AsyncSession(conn, expire_on_commit=False)

        # Make commit() roll back to the savepoint instead of flushing to DB
        async def patched_commit():
            nonlocal nested
            await session.flush()
            nested = await conn.begin_nested()  # new SAVEPOINT after flush

        session.commit = patched_commit  # type: ignore[method-assign]

        try:
            yield session
        finally:
            await session.close()
            await conn.rollback()  # rolls back everything


# ---------------------------------------------------------------------------
# HTTP client with the test DB session injected
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Faker
# ---------------------------------------------------------------------------
@pytest.fixture
def faker() -> Faker:
    return Faker()
