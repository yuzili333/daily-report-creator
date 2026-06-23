#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export OUTPUT_ROOT="${OUTPUT_ROOT:-${ROOT_DIR}/output}"
export LOG_ROOT="${LOG_ROOT:-${ROOT_DIR}/logs}"
export TMP_ROOT="${TMP_ROOT:-${ROOT_DIR}/tmp}"

exec "${ROOT_DIR}/deploy/entrypoint.sh" "${1:-collect}"
