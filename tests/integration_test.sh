#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-.env.example}"
INTEGRATION_TIMEOUT_SECONDS="${INTEGRATION_TIMEOUT_SECONDS:-120}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Environment file not found: $ENV_FILE"
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "$ENV_FILE"
set +a

frontend_url="http://127.0.0.1:${FRONTEND_PORT}"
deadline=$((SECONDS + INTEGRATION_TIMEOUT_SECONDS))

echo "Waiting for frontend health endpoint..."
healthy=0
while (( SECONDS < deadline )); do
  if curl -fsS "${frontend_url}/healthz" >/dev/null; then
    healthy=1
    break
  fi
  sleep 1
done

if [[ "$healthy" -ne 1 ]]; then
  echo "Frontend did not become healthy in time"
  exit 1
fi

job_id="$(curl -fsS -X POST "${frontend_url}/submit" | python -c "import json,sys; print(json.load(sys.stdin)['job_id'])")"
echo "Submitted job: ${job_id}"

while (( SECONDS < deadline )); do
  status="$(curl -fsS "${frontend_url}/status/${job_id}" | python -c "import json,sys; print(json.load(sys.stdin).get('status',''))")"
  if [[ "$status" == "completed" ]]; then
    echo "Integration test passed: job completed"
    exit 0
  fi
  sleep 2
done

echo "Integration test failed: job ${job_id} did not complete in time"
exit 1
