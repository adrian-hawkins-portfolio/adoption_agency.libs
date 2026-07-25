import logging
import sys

from petstore_common.util.correlation_guid import correlation_guid


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = correlation_guid.get()
        return True

def setup_logging():
    formatter = logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(request_id)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(RequestIdFilter())

    root.addHandler(console_handler)

    for name in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi", "backoffice_api"]:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG if name == "backoffice_api" else logging.INFO)
        logger.propagate = True
        logger.handlers.clear()

    return logging.getLogger("backoffice_api")


logger = setup_logging()