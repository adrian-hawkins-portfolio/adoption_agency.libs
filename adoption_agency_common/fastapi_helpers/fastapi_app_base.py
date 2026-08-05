import asyncio
from typing import Annotated, Sequence, Any

import uvicorn
import socket
from fastapi import FastAPI,status

from adoption_agency_common.fastapi_helpers.endpoints.health import health
from adoption_agency_common.fastapi_helpers.endpoints.metrics import metrics
from adoption_agency_common.fastapi_helpers.exception_handlers.timeout_handler import timeout_handler
from adoption_agency_common.fastapi_helpers.middleware.prometheus_metrics_middleware import prometheus_middleware
from adoption_agency_common.fastapi_helpers.models.boa_models import BoaResponseModel
from adoption_agency_common.saga_manager.saga_node import SagaNode
from adoption_agency_common.util import logger
from adoption_agency_common.fastapi_helpers.lifecycles import boa_lifespan
from adoption_agency_common.fastapi_helpers.middleware.request_guid_middleware import request_guid_middleware


class BOAFastApi(FastAPI):
    def __init__(self, node: SagaNode, is_service: bool = False, **extra):
        default_responses = {
            status.HTTP_408_REQUEST_TIMEOUT: {
                "model": BoaResponseModel[str],
                "description": "Request Timeout",
            }
        }
        if "responses" in extra:
            default_responses.update(extra["responses"])
        extra["responses"] = default_responses

        super().__init__(**extra, lifespan=boa_lifespan)
        self.middleware("http")(request_guid_middleware)
        self.middleware("http")(prometheus_middleware)
        # Don't generate openapi docs, so when generating client code, this isn't accessible
        self.get("/metrics", include_in_schema=False)(metrics)
        self.get("/health", include_in_schema=False)(health)
        self.exception_handler(asyncio.TimeoutError)(timeout_handler)
        self.node = node

    def _get_available_port(self, preferred_port: int) -> int:
        """Returns the preferred port if available, otherwise an ephemeral port."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", preferred_port))
                return preferred_port
            except OSError:
                # Let the OS choose an available port
                sock.bind(("127.0.0.1", 0))
                return sock.getsockname()[1]

    def run(self, port:int = 8080):
        open_port = self._get_available_port(port)
        uvicorn.run(self,
                    host="127.0.0.1",
                    port=open_port,
                    log_level="info",
                    access_log=True,  # Keep access logs
                    log_config=None
                    )

    def include_router(self, router, *, prefix: str = "", **kwargs):
        super().include_router(router, prefix=prefix, **kwargs)
        for route in router.routes:
            logger.debug(f"Registering route: {prefix}{route.path}  [{route.name}]")

