from typing import Any, Optional

from pydantic import BaseModel, Field

from adoption_agency_common.util import correlation_guid


class MessageHeaders(BaseModel):
    guid: Optional[str] = None
    callback_queue: Optional[str] = None

class BaseMessage(BaseModel):
    headers: MessageHeaders = Field(default_factory=MessageHeaders)

    @staticmethod
    def get_message_name(cls) -> str:
        return cls.__name__
