from fastapi import Request

import uuid

from adoption_agency_common.util import logger, correlation_guid


async def request_guid_middleware(request: Request, call_next):
    correlation_guid.set(str(uuid.uuid4()))
    logger.debug("Incoming request")
    response = await call_next(request)
    return response