#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE_NAME="${IMAGE_NAME:-ai-tech-daily-brief}"
VERSION="${VERSION:-v$(date '+%Y.%m.%d')-1}"
PLATFORM="${PLATFORM:-linux/amd64}"
OUTPUT_DIR="${OUTPUT_DIR:-${ROOT_DIR}/dist/images}"
DOCKERFILE="${DOCKERFILE:-${ROOT_DIR}/deploy/Dockerfile}"
NO_CACHE=0
SKIP_SMOKE=0

usage() {
  cat <<EOF
Usage: $0 [options]

Build ai-tech-daily-brief Docker image locally and export it as a .tar.gz file.

Options:
  --image-name NAME     Docker image name. Default: ${IMAGE_NAME}
  --version VERSION     Explicit image tag. Default: ${VERSION}
  --platform PLATFORM   Docker build platform. Default: ${PLATFORM}
  --output-dir DIR      Directory for exported image file. Default: ${OUTPUT_DIR}
  --dockerfile FILE     Dockerfile path. Default: ${DOCKERFILE}
  --no-cache            Build without Docker layer cache
  --skip-smoke          Skip post-build Python compile smoke test
  -h, --help            Show this help

Environment variables with the same names can also be used:
  IMAGE_NAME, VERSION, PLATFORM, OUTPUT_DIR, DOCKERFILE
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image-name)
      IMAGE_NAME="$2"
      shift 2
      ;;
    --version)
      VERSION="$2"
      shift 2
      ;;
    --platform)
      PLATFORM="$2"
      shift 2
      ;;
    --output-dir)
      OUTPUT_DIR="$2"
      shift 2
      ;;
    --dockerfile)
      DOCKERFILE="$2"
      shift 2
      ;;
    --no-cache)
      NO_CACHE=1
      shift
      ;;
    --skip-smoke)
      SKIP_SMOKE=1
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

if [[ -z "${VERSION}" || "${VERSION}" == "latest" ]]; then
  echo "VERSION must be an explicit non-latest tag" >&2
  exit 2
fi

if [[ ! -f "${DOCKERFILE}" ]]; then
  echo "Dockerfile not found: ${DOCKERFILE}" >&2
  exit 2
fi

IMAGE_REF="${IMAGE_NAME}:${VERSION}"
SAFE_IMAGE_NAME="${IMAGE_NAME//\//-}"
SAFE_IMAGE_NAME="${SAFE_IMAGE_NAME//:/-}"
ARTIFACT="${OUTPUT_DIR}/${SAFE_IMAGE_NAME}-${VERSION}.tar.gz"

BUILD_ARGS=(
  docker build
  --platform "${PLATFORM}"
  -f "${DOCKERFILE}"
  -t "${IMAGE_REF}"
)

if [[ "${NO_CACHE}" == "1" ]]; then
  BUILD_ARGS+=(--no-cache)
fi

BUILD_ARGS+=("${ROOT_DIR}")

echo "building image: ${IMAGE_REF}"
"${BUILD_ARGS[@]}"

if [[ "${SKIP_SMOKE}" != "1" ]]; then
  echo "running smoke test: python -m compileall app"
  docker run --rm --entrypoint python "${IMAGE_REF}" -m compileall app
fi

mkdir -p "${OUTPUT_DIR}"
echo "exporting image: ${ARTIFACT}"
docker save "${IMAGE_REF}" | gzip > "${ARTIFACT}"

cat <<EOF
Build complete.

Image: ${IMAGE_REF}
Artifact: ${ARTIFACT}

Upload example:
  scripts/upload-image-to-ecs.sh --host <ecs-ip-or-domain> --artifact "${ARTIFACT}" --image "${IMAGE_REF}"
EOF
