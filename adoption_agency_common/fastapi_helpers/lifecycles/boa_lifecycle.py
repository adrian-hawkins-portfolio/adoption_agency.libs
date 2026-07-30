from contextlib import asynccontextmanager, AsyncExitStack

from fastapi import FastAPI
from adoption_agency_common.fastapi_helpers.lifecycles.database_lifecycle import database_lifecycle
from adoption_agency_common.fastapi_helpers.lifecycles.endpoint_lifecycle import endpoint_lifespan
from adoption_agency_common.fastapi_helpers.lifecycles.node_lifecycle import node_lifespan
from adoption_agency_common.util import logger



@asynccontextmanager
async def boa_lifespan(app: FastAPI):
    lifecycles = [database_lifecycle, node_lifespan]
    logger.debug("Starting app...")
    async with AsyncExitStack() as stack:
        for lifecycle in lifecycles:
            await stack.enter_async_context(lifecycle(app))
        yield
    # print("Starting application...")
    #
    # # Example: initialize resources
    # app.state.db = "database_connection"
    # app.state.cache = {}
    #
    # yield
    #
    # # Shutdown
    # print("Shutting down application...")
    #
    # # Example: clean up resources
    # app.state.db = None
    # app.state.cache.clear()
