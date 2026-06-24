#!/usr/bin/env bash
set -euo pipefail

UNIT_NAME="${1:-unknown.service}"
RUN_DATE="$(date '+%Y-%m-%d')"
STATE_ROOT="${STATE_ROOT:-/var/lib/ai-tech-daily-brief/state}"
LOG_ROOT="${LOG_ROOT:-/var/log/ai-tech-daily-brief}"
FAILURE_LOG="${LOG_ROOT}/failure.log"

PHASE="task"
case "${UNIT_NAME}" in
  *push*)
    PHASE="push"
    ;;
  *collect*)
    PHASE="collect"
    ;;
esac

FAILED_MARKER="${STATE_ROOT}/${RUN_DATE}.${PHASE}.failed"

mkdir -p "${STATE_ROOT}" "${LOG_ROOT}"

{
  echo "status=failed"
  echo "date=${RUN_DATE}"
  echo "timestamp=$(date '+%Y-%m-%dT%H:%M:%S%z')"
  echo "unit=${UNIT_NAME}"
  echo "phase=${PHASE}"
  echo "detail=systemd unit failed before successful completion"
} >"${FAILED_MARKER}"

{
  echo "[$(date '+%Y-%m-%dT%H:%M:%S%z')] ${UNIT_NAME} failed"
  if command -v systemctl >/dev/null 2>&1; then
    systemctl status "${UNIT_NAME}" --no-pager || true
  fi
} >>"${FAILURE_LOG}" 2>&1

echo "recorded failure marker: ${FAILED_MARKER}"
