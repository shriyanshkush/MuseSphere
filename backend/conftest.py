import asyncio
import os
import sys
import pytest
from app.database.session import Base, engine

sys.path.insert(0, os.path.abspath("."))


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """
    Initialize SQLite test database schema before running test suite
    and drop tables upon completion.
    """
    async def init_models() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_models())
    yield
    async def drop_models() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(drop_models())
