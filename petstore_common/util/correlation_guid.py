from contextvars import ContextVar

correlation_guid: ContextVar[str] = ContextVar("correlation_guid", default="-")