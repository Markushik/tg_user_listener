from __future__ import annotations

import logging
from contextvars import ContextVar
from typing import Optional, Any

from pydantic import BaseModel


class BusinessContext(BaseModel):
    user_id: Optional[int] = None
    chat_id: Optional[int] = None


context: ContextVar[BusinessContext] = ContextVar(
    "business_context", default=BusinessContext()
)


def set_context(*, user_id: Optional[int] = None, chat_id: Optional[int] = None) -> None:
    current = context.get()
    data = current.model_dump()
    
    if user_id is not None:
        data["user_id"] = user_id
    if chat_id is not None:
        data["chat_id"] = chat_id
        
    context.set(BusinessContext(**data))


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
            "[user_id=%(user_id)s chat_id=%(chat_id)s] "
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
