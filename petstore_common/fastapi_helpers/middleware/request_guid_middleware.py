from fastapi import Request

import uuid

from petstore_common.util import logger, correlation_guid


async def request_guid_middleware(request: Request, call_next):
    correlation_guid.set(str(uuid.uuid4()))
    logger.debug("Incoming request")
    # start_time = time.perf_counter()
    response = await call_next(request)
    # process_time = time.perf_counter() - start_time
    # response.headers["X-Process-Time"] = str(process_time)
    return response