#!/usr/bin/env bash
set -euo pipefail

NEW_IMAGE="${1:?Usage: rolling_update.sh <image-ref>}"
SERVICE_NAME="${2:-frontend-prod}"
TIMEOUT_SECONDS="${3:-60}"
CANDIDATE_PORT="${4:-13000}"

CANDIDATE_NAME="${SERVICE_NAME}-candidate-$(date +%s)"

echo "Starting candidate container ${CANDIDATE_NAME} from ${NEW_IMAGE}"
docker run -d --name "${CANDIDATE_NAME}" -p "${CANDIDATE_PORT}:3000" "${NEW_IMAGE}" >/dev/null

healthy=0
for _ in $(seq 1 "$TIMEOUT_SECONDS"); do
  status="$(docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "${CANDIDATE_NAME}")"
  if [[ "$status" == "healthy" ]]; then
    healthy=1
    break
  fi
  if [[ "$status" == "unhealthy" ]]; then
    break
  fi
  sleep 1
done

if [[ "$healthy" -ne 1 ]]; then
  echo "Candidate failed health checks within ${TIMEOUT_SECONDS}s; keeping old container running"
  docker rm -f "${CANDIDATE_NAME}" >/dev/null
  exit 1
fi

echo "Candidate is healthy; stopping old container"
if docker ps -a --format '{{.Names}}' | grep -q "^${SERVICE_NAME}$"; then
  docker rm -f "${SERVICE_NAME}" >/dev/null
fi

docker rename "${CANDIDATE_NAME}" "${SERVICE_NAME}"
echo "Rolling update completed successfully"
