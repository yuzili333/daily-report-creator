#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ECS_USER="${ECS_USER:-root}"
ECS_HOST="${ECS_HOST:-}"
ECS_PORT="${ECS_PORT:-22}"
REMOTE_DIR="${REMOTE_DIR:-/opt/ai-tech-daily-brief}"
ARTIFACT="${ARTIFACT:-}"
IMAGE_REF="${IMAGE_REF:-}"
SSH_KEY="${SSH_KEY:-}"
UPLOAD_DEPLOY=1

usage() {
  cat <<EOF
Usage: $0 --host HOST --artifact FILE [options]

Upload a locally exported ai-tech-daily-brief Docker image artifact to ECS.

Required:
  --host HOST          ECS public IP or domain
  --artifact FILE      Local .tar.gz image artifact from scripts/build-image.sh

Options:
  --user USER          SSH user. Default: ${ECS_USER}
  --port PORT          SSH port. Default: ${ECS_PORT}
  --remote-dir DIR     Remote app directory. Default: ${REMOTE_DIR}
  --image IMAGE        Image reference, for display and env guidance
  --identity-file KEY  SSH private key path
  --artifact-only      Upload only the image artifact, not deploy/config files
  -h, --help           Show this help

Environment variables with the same names can also be used:
  ECS_USER, ECS_HOST, ECS_PORT, REMOTE_DIR, ARTIFACT, IMAGE_REF, SSH_KEY
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --host)
      ECS_HOST="$2"
      shift 2
      ;;
    --artifact)
      ARTIFACT="$2"
      shift 2
      ;;
    --user)
      ECS_USER="$2"
      shift 2
      ;;
    --port)
      ECS_PORT="$2"
      shift 2
      ;;
    --remote-dir)
      REMOTE_DIR="$2"
      shift 2
      ;;
    --image)
      IMAGE_REF="$2"
      shift 2
      ;;
    --identity-file)
      SSH_KEY="$2"
      shift 2
      ;;
    --artifact-only)
      UPLOAD_DEPLOY=0
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${ECS_HOST}" ]]; then
  echo "--host is required" >&2
  usage >&2
  exit 2
fi

if [[ -z "${ARTIFACT}" ]]; then
  echo "--artifact is required" >&2
  usage >&2
  exit 2
fi

if [[ ! -f "${ARTIFACT}" ]]; then
  echo "artifact not found: ${ARTIFACT}" >&2
  exit 2
fi

SSH_ARGS=(-p "${ECS_PORT}")
SCP_ARGS=(-P "${ECS_PORT}")
if [[ -n "${SSH_KEY}" ]]; then
  SSH_ARGS+=(-i "${SSH_KEY}")
  SCP_ARGS+=(-i "${SSH_KEY}")
fi

REMOTE="${ECS_USER}@${ECS_HOST}"
REMOTE_ARTIFACT="${REMOTE_DIR}/$(basename "${ARTIFACT}")"

echo "creating remote directory: ${REMOTE}:${REMOTE_DIR}"
ssh "${SSH_ARGS[@]}" "${REMOTE}" "mkdir -p '${REMOTE_DIR}'"

echo "uploading image artifact: ${ARTIFACT}"
scp "${SCP_ARGS[@]}" "${ARTIFACT}" "${REMOTE}:${REMOTE_ARTIFACT}"

if [[ "${UPLOAD_DEPLOY}" == "1" ]]; then
  echo "uploading deploy and config templates"
  scp "${SCP_ARGS[@]}" -r "${ROOT_DIR}/deploy" "${ROOT_DIR}/config" "${REMOTE}:${REMOTE_DIR}/"
fi

cat <<EOF
Upload complete.

Remote artifact:
  ${REMOTE_ARTIFACT}

Load image on ECS:
  gzip -dc "${REMOTE_ARTIFACT}" | docker load

Verify loaded image:
  docker images | grep ai-tech-daily-brief
EOF

if [[ -n "${IMAGE_REF}" ]]; then
  cat <<EOF

Set this in /etc/ai-tech-daily-brief/env:
  AI_TECH_DAILY_BRIEF_IMAGE=${IMAGE_REF}
EOF
fi
