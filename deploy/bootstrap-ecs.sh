#!/usr/bin/env bash
set -euo pipefail

APP_USER="ai-brief"
APP_UID="10001"
APP_DIR="/opt/ai-tech-daily-brief"
OUTPUT_DIR="/var/lib/ai-tech-daily-brief/output"
LOG_DIR="/var/log/ai-tech-daily-brief"
ENV_DIR="/etc/ai-tech-daily-brief"
ENV_FILE="${ENV_DIR}/env"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ "$(id -u)" != "0" ]]; then
  echo "bootstrap-ecs.sh must run as root" >&2
  exit 1
fi

if ! id "${APP_USER}" >/dev/null 2>&1; then
  useradd --system --uid "${APP_UID}" --home-dir "${APP_DIR}" --shell /usr/sbin/nologin "${APP_USER}"
fi

mkdir -p "${APP_DIR}" "${OUTPUT_DIR}" "${LOG_DIR}" "${ENV_DIR}"
chown -R "${APP_USER}:${APP_USER}" "${OUTPUT_DIR}" "${LOG_DIR}"
chmod 755 "${APP_DIR}" "${OUTPUT_DIR}" "${LOG_DIR}"
chmod 700 "${ENV_DIR}"

if [[ ! -f "${ENV_FILE}" ]]; then
  install -m 600 "${REPO_DIR}/config/.env.example" "${ENV_FILE}"
  echo "created ${ENV_FILE}; edit secrets and AI_TECH_DAILY_BRIEF_IMAGE before enabling timers"
else
  chmod 600 "${ENV_FILE}"
fi

install -m 644 "${SCRIPT_DIR}/systemd/ai-tech-daily-brief-collect.service" /etc/systemd/system/
install -m 644 "${SCRIPT_DIR}/systemd/ai-tech-daily-brief-collect.timer" /etc/systemd/system/
install -m 644 "${SCRIPT_DIR}/systemd/ai-tech-daily-brief-push.service" /etc/systemd/system/
install -m 644 "${SCRIPT_DIR}/systemd/ai-tech-daily-brief-push.timer" /etc/systemd/system/

timedatectl set-timezone Asia/Shanghai || true
systemctl daemon-reload

cat <<'EOF'
Bootstrap complete.

Next steps:
1. Edit /etc/ai-tech-daily-brief/env and set secrets plus AI_TECH_DAILY_BRIEF_IMAGE.
2. Validate the image and env:
   docker pull "$AI_TECH_DAILY_BRIEF_IMAGE"
   docker run --rm --env-file /etc/ai-tech-daily-brief/env "$AI_TECH_DAILY_BRIEF_IMAGE" validate-env
   docker run --rm --env-file /etc/ai-tech-daily-brief/env "$AI_TECH_DAILY_BRIEF_IMAGE" validate-summary-model
   docker run --rm --env-file /etc/ai-tech-daily-brief/env "$AI_TECH_DAILY_BRIEF_IMAGE" validate-smtp
3. Enable timers:
   systemctl enable --now ai-tech-daily-brief-collect.timer
   systemctl enable --now ai-tech-daily-brief-push.timer
EOF
