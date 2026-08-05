import asyncio

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from adoption_agency_common.fastapi_helpers.models.boa_models import BoaResponseModel
from adoption_agency_common.util import logger


async def timeout_handler(request: Request, exc: asyncio.TimeoutError):
    logger.debug("Sending timeout response")
    error_payload = BoaResponseModel[str](response="Timeout", code=status.HTTP_408_REQUEST_TIMEOUT)

    return JSONResponse(
        status_code=status.HTTP_408_REQUEST_TIMEOUT,
        content=error_payload.model_dump()
    )