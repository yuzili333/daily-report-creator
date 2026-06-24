#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -z "${APP_DIR:-}" ]]; then
  if [[ -d /app/app ]]; then
    APP_DIR="/app"
  else
    APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
  fi
fi

cd "${APP_DIR}"

mkdir -p "${OUTPUT_ROOT:-/app/output}" "${LOG_ROOT:-/app/logs}" "${TMP_ROOT:-/app/tmp}" "${STATE_ROOT:-/app/state}"

case "${1:-}" in
  collect)
    python -m app.validate_env
    python -m app.collect
    ;;
  push)
    python -m app.validate_env
    python -m app.push
    ;;
  validate-env)
    python -m app.validate_env
    ;;
  validate-summary-model)
    python -m app.validate_summary_model --check-connectivity
    ;;
  validate-smtp)
    shift || true
    python -m app.smtp_delivery "$@"
    ;;
  *)
    echo "Usage: entrypoint.sh {collect|push|validate-env|validate-summary-model|validate-smtp}" >&2
    exit 2
    ;;
esac
