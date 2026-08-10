import pytest_asyncio
from app.core.database import init_db


@pytest_asyncio.fixture(autouse=True, scope="session")
async def prepare_database():
    """Ensure database tables are initialized once for the entire test session without table locking."""
    await init_db()
