from typing import Any

from adoption_agency_common.util import correlation_guid


class BaseMessage:

    def __init__(self, payload=None):
        if payload is None:
            payload = {}
        self._guid = correlation_guid.get()
        self.payload = payload
        self.headers = {}

    @property
    def guid(self):
        return correlation_guid

    @staticmethod
    def get_message_name(cls) -> str:
        return cls.__name__