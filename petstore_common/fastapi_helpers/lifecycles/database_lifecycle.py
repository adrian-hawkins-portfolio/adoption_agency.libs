from contextlib import asynccontextmanager

from petstore_common.util import logger
from petstore_common.database import _startup_db


@asynccontextmanager
async def database_lifecycle():
    logger.debug("Opening up database connections")
    await _startup_db()
    yield
    logger.debug("Shutting down database connections")