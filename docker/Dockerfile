FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# system deps (часто нужны для wheels; можно упростить позже)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
  && rm -rf /var/lib/apt/lists/*

# Poetry
RUN pip install --no-cache-dir poetry

# Dependencies first (better cache)
COPY pyproject.toml poetry.lock* /app/
RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --only main --no-root

# App code
COPY src /app/src
ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "tg_user_forwarder.main.app:app", "--host", "0.0.0.0", "--port", "8000"]