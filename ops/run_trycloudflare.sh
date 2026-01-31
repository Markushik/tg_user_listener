#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-8000}"
WEBHOOK_PATH="${WEBHOOK_PATH:-/telegram/webhook}"

WEBHOOK_SECRET="${WEBHOOK_SECRET:-my-secret}"

export OTEL_TRACES_EXPORTER="${OTEL_TRACES_EXPORTER:-none}"

LOG="$(mktemp /tmp/cloudflared.XXXXXX.log)"

cleanup() {
  [[ -n "${CF_PID:-}" ]] && kill "$CF_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo "Starting cloudflared quick tunnel..."
cloudflared tunnel --url "http://127.0.0.1:${PORT}" 2>&1 | tee "$LOG" &
CF_PID=$!

echo "Waiting for trycloudflare URL..."
URL=""
for _ in {1..300}; do
  URL="$(grep -oE 'https://[-a-z0-9]+\.trycloudflare\.com' "$LOG" | tail -n1 || true)"
  [[ -n "$URL" ]] && break
  sleep 0.1
done

if [[ -z "$URL" ]]; then
  echo "ERROR: trycloudflare URL not found in logs: $LOG" >&2
  exit 1
fi

echo "TRYCLOUDFLARE URL: $URL"

HOST="${URL#https://}"
echo "Waiting DNS for $HOST (to avoid Telegram 'Failed to resolve host')..."
for _ in {1..60}; do
  if getent hosts "$HOST" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

export WEBHOOK_BASE_URL="$URL"
export WEBHOOK_PATH="$WEBHOOK_PATH"
export WEBHOOK_SECRET="$WEBHOOK_SECRET"

echo "Starting app on :$PORT with WEBHOOK_BASE_URL=$WEBHOOK_BASE_URL"

exec opentelemetry-instrument --log_level info \
  python -m uvicorn tg_user_forwarder.main.app:app --host 0.0.0.0 --port "$PORT"
