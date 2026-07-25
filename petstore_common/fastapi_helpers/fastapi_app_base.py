from typing import Annotated

import uvicorn
from fastapi import FastAPI

from petstore_common.fastapi_helpers.lifecycles import boa_lifespan
from petstore_common.fastapi_helpers.middleware.request_guid_middleware import request_guid_middleware


class BOAFastApi(FastAPI):
    def __init__(self, **extra):
        super().__init__(**extra, lifespan=boa_lifespan)
        self.middleware("http")(request_guid_middleware)

    def run(self, port:int = 8080):
        uvicorn.run(self, host="0.0.0.0", port=port)