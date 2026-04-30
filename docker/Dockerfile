# syntax=docker/dockerfile:1.6
FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml requirements.lock ./
RUN touch README.md
RUN uv pip install --no-cache --system -r requirements.lock

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY src /app/src

RUN useradd -r -u 10001 app
USER app

ENTRYPOINT ["opentelemetry-instrument", "--log_level", "info"]
CMD ["python", "-m", "uvicorn", "tg_user_forwarder.main.app:app", "--host", "0.0.0.0", "--port", "8080"]
