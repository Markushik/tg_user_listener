#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-9000}"
WEBHOOK_PATH="${WEBHOOK_PATH:-/telegram/webhook}"
WEBHOOK_SECRET="${WEBHOOK_SECRET:-my-secret}"

# ТВОЙ ТОКЕН (как ты прислал)
BOT_TOKEN="${BOT_TOKEN:-6996207760:AAEQbsRpJCuWp7bKAfk24t7RecPqskBLpZQ}"

# Если хочешь всё-таки через OTel — поставь USE_OTEL=1 и убедись что команда не пустая
USE_OTEL="${USE_OTEL:-0}"

LOG="$(mktemp /tmp/cloudflared.XXXXXX.log)"

cleanup() {
  [[ -n "${CF_PID:-}" ]] && kill "$CF_PID" 2>/dev/null || true
}
trap cleanup EXIT

tg_api() {
  local method="$1"
  shift || true
  curl -fsS "https://api.telegram.org/bot${BOT_TOKEN}/${method}" "$@"
}

echo "1) Starting cloudflared quick tunnel -> http://127.0.0.1:${PORT}"
cloudflared tunnel --url "http://127.0.0.1:${PORT}" 2>&1 | tee "$LOG" &
CF_PID=$!

echo "2) Waiting for trycloudflare URL..."
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

echo "3) Waiting DNS for $HOST (avoid Telegram 'Failed to resolve host')..."
for _ in {1..60}; do
  if getent hosts "$HOST" >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

export WEBHOOK_BASE_URL="$URL"
export WEBHOOK_PATH="$WEBHOOK_PATH"
export WEBHOOK_SECRET="$WEBHOOK_SECRET"

WEBHOOK_URL="${URL}${WEBHOOK_PATH}"

echo "4) Setting Telegram webhook to: $WEBHOOK_URL"
# drop_pending_updates=true — чтобы не копились старые апдейты на неверный URL
tg_api "setWebhook" \
  -d "url=${WEBHOOK_URL}" \
  -d "secret_token=${WEBHOOK_SECRET}" \
  -d "drop_pending_updates=true" \
  | tee /tmp/tg_set_webhook.json

echo "5) getWebhookInfo:"
tg_api "getWebhookInfo" | tee /tmp/tg_get_webhook_info.json
echo

echo "6) exec: starting app on :$PORT"
if [[ "$USE_OTEL" == "1" ]]; then
  exec opentelemetry-instrument --log_level info \
    python -m uvicorn tg_user_forwarder.main.app:app --host 0.0.0.0 --port "$PORT"
else
  exec python -m uvicorn tg_user_forwarder.main.app:app --host 0.0.0.0 --port "$PORT"
fi