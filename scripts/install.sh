#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="/opt/tg_user_listener"
SERVICE_NAME="tg_user_listener.service"
SERVICE_DST="/etc/systemd/system/${SERVICE_NAME}"

REPO_URL="https://github.com/Markushik/tg_user_listener"
BRANCH="k8s"
UNIT_REL_PATH="scripts/tg_user_listener.service"

git config --global --add safe.directory "$PROJECT_DIR" >/dev/null 2>&1 || true

if [[ -d "$PROJECT_DIR/.git" ]]; then
  git -C "$PROJECT_DIR" remote set-url origin "$REPO_URL"
  git -C "$PROJECT_DIR" config remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'
  git -C "$PROJECT_DIR" fetch --prune origin "$BRANCH"
  git -C "$PROJECT_DIR" reset --hard "origin/$BRANCH"
  git -C "$PROJECT_DIR" clean -fdx
else
  rm -rf "$PROJECT_DIR"
  git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$PROJECT_DIR"
fi

UNIT_SRC="$PROJECT_DIR/$UNIT_REL_PATH"
if [[ ! -f "$UNIT_SRC" ]]; then
  echo "Unit file not found: $UNIT_SRC"
  exit 1
fi

cp -f "$UNIT_SRC" "$SERVICE_DST"
chmod 0644 "$SERVICE_DST"

systemctl daemon-reload
systemctl enable --now "$SERVICE_NAME"
systemctl restart "$SERVICE_NAME"
systemctl --no-pager status "$SERVICE_NAME" || true

echo "journalctl -fu $SERVICE_NAME"