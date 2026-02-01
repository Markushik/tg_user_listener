from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional, Any

from pydantic import BaseModel


class BusinessContext(BaseModel):
    update_id: Optional[int] = None
    user_id: Optional[int] = None
    chat_id: Optional[int] = None


context: ContextVar[BusinessContext] = ContextVar(
    "business_context", default=BusinessContext()
)


def set_context(
    *,
    update_id: Optional[int] = None,
    user_id: Optional[int] = None,
    chat_id: Optional[int] = None,
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
    update_id: Optional[int] = None,
    user_id: Optional[int] = None,
    chat_id: Optional[int] = None,
):
    token = context.set(
        BusinessContext(
            update_id=update_id,
            user_id=user_id,
            chat_id=chat_id,
        )
    )
    try:
        yield
    finally:
        context.reset(token)


class ContextFilter(logging.Filter):
    @staticmethod
    def norm(value: Any) -> Optional[str]:
        if value in (None, "", "-", 0, "0"):
            return None
        return str(value)

    def filter(self, record: logging.LogRecord) -> bool:
        ctx = context.get()

        trace_id = self.norm(getattr(record, "trace_id", None)) or self.norm(getattr(record, "otelTraceID", None))
        span_id = self.norm(getattr(record, "span_id", None)) or self.norm(getattr(record, "otelSpanID", None))

        record.trace_id = trace_id or "-"
        record.span_id = span_id or "-"

        record.update_id = getattr(record, "update_id", None) or ctx.update_id or "-"
        record.user_id = getattr(record, "user_id", None) or ctx.user_id or "-"
        record.chat_id = getattr(record, "chat_id", None) or ctx.chat_id or "-"

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
