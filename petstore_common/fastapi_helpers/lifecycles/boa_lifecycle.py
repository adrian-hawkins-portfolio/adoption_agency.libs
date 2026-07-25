from contextlib import asynccontextmanager, AsyncExitStack

# from petstore_common import BOAFastApi
from petstore_common.fastapi_helpers.lifecycles.database_lifecycle import database_lifecycle


class FastApi:
    pass


@asynccontextmanager
async def boa_lifespan(app: FastApi):
    lifecycles = [database_lifecycle]
    async with AsyncExitStack() as stack:
        for lifecycle in lifecycles:
            await stack.enter_async_context(lifecycle())
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
