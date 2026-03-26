from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from opentelemetry import trace
from opentelemetry.trace import format_span_id, format_trace_id
from pydantic import BaseModel


class BusinessContext(BaseModel):
    update_id: int | None = None
    user_id: int | None = None
    chat_id: int | None = None


context: ContextVar[BusinessContext] = ContextVar(
    "business_context",
    default=BusinessContext(),
)


def set_context(
    *,
    update_id: int | None = None,
    user_id: int | None = None,
    chat_id: int | None = None,
) -> None:
    current = context.get()
    data = current.model_dump()

    if update_id is not None:
        data["update_id"] = update_id
    if user_id is not None:
        data["user_id"] = user_id
    if chat_id is not None:
        data["chat_id"] = chat_id

    context.set(BusinessContext(**data))


@contextmanager
def context_scope(
    *,
    update_id: int | None = None,
    user_id: int | None = None,
    chat_id: int | None = None,
):
    current = context.get()
    data = current.model_dump()

    if update_id is not None:
        data["update_id"] = update_id
    if user_id is not None:
        data["user_id"] = user_id
    if chat_id is not None:
        data["chat_id"] = chat_id

    token = context.set(BusinessContext(**data))
    try:
        yield
    finally:
        context.reset(token)


class ContextFilter(logging.Filter):
    @staticmethod
    def norm(value: Any) -> str | None:
        if value in (None, "", "-", 0, "0"):
            return None
        return str(value)

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = context.get()

        current_span = trace.get_current_span()
        span_context = current_span.get_span_context()

        otel_trace_id = None
        otel_span_id = None
        if span_context.is_valid:
            otel_trace_id = format_trace_id(span_context.trace_id)
            otel_span_id = format_span_id(span_context.span_id)

        record.trace_id = (
            self.norm(getattr(record, "trace_id", None))
            or self.norm(getattr(record, "otelTraceID", None))
            or otel_trace_id
            or "-"
        )
        record.span_id = (
            self.norm(getattr(record, "span_id", None))
            or self.norm(getattr(record, "otelSpanID", None))
            or otel_span_id
            or "-"
        )

        record.update_id = self.norm(getattr(record, "update_id", None)) or self.norm(ctx.update_id) or "-"
        record.user_id = self.norm(getattr(record, "user_id", None)) or self.norm(ctx.user_id) or "-"
        record.chat_id = self.norm(getattr(record, "chat_id", None)) or self.norm(ctx.chat_id) or "-"

        return True


def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()

    if getattr(root, "_logging_inited", False):
        return

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] "
            "[trace_id=%(trace_id)s span_id=%(span_id)s] "
            "[update_id=%(update_id)s user_id=%(user_id)s chat_id=%(chat_id)s] "
            "%(name)s - %(message)s"
        )
    )
    handler.addFilter(ContextFilter())

    root.setLevel(level)
    root.addHandler(handler)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers = [handler]
        logger.propagate = False
        logger.setLevel(level)

    logging.getLogger("opentelemetry").setLevel(logging.ERROR)
    root._logging_inited = True
