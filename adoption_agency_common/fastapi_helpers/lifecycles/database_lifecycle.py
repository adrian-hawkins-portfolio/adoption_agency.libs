from contextlib import asynccontextmanager

from fastapi import FastAPI

from adoption_agency_common.util import logger
from adoption_agency_common.database import _startup_db


@asynccontextmanager
async def database_lifecycle(app: FastAPI):
    logger.debug("Opening up database connections")
    await _startup_db()
    yield
    logger.debug("Shutting down database connections")