from pydantic import BaseModel, Field
from fastapi import status
from typing import Generic, TypeVar

from adoption_agency_common.util import correlation_guid

T = TypeVar("T")

class BoaResponseModel(BaseModel, Generic[T]):
    unique_reference: str = Field(default_factory=correlation_guid.get)
    response: T
    code: int = status.HTTP_200_OK

class TimeoutErrorResponse(BaseModel):
    error: str = "Request Timeout"
    detail: str = "The request took too long to process."
    code: int = status.HTTP_408_REQUEST_TIMEOUT