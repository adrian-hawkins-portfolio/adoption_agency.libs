import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine(
    os.getenv("DATABASE_CONNECTION_STRING"),
    echo=os.getenv("DEBUG_DB") == "True",
)

session_local = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)

async def _startup_db():
    async with async_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))