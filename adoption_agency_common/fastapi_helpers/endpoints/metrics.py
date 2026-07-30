from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from fastapi.responses import PlainTextResponse

def metrics():
    return PlainTextResponse(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )