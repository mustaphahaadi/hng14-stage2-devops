# hng14-stage2-devops

Containerized job processing stack with four services:
- `frontend` (Express UI/API proxy)
- `api` (FastAPI job API)
- `worker` (Redis queue consumer)
- `redis` (queue and status store)

## Prerequisites

Install the following on a clean machine:
- Git
- Docker Engine (24+ recommended)
- Docker Compose v2 (included as `docker compose` in recent Docker installs)
- Bash and curl (usually preinstalled on Linux/macOS)

Optional for local lint/tests outside containers:
- Python 3.11+
- Node.js 22+

## 1. Clone the repository

```bash
git clone https://github.com/chukwukelu2023/hng14-stage2-devops.git
cd hng14-stage2-devops
```

## 2. Create local environment file

```bash
cp .env.example .env
```

Adjust values in `.env` if needed (ports, image names, limits). Do not commit `.env`.

## 3. Build and start the full stack

Use either compose file. `docker-compose.yml` is provided for tooling compatibility; `compose.yaml` has equivalent service definitions.

```bash
docker compose --env-file .env -f docker-compose.yml up -d --build
```

## 4. Verify startup success

Check containers:

```bash
docker compose --env-file .env -f docker-compose.yml ps
```

Expected:
- All services are up: `redis`, `api`, `worker`, `frontend`
- Health status shows healthy for services with health checks

Check HTTP health endpoints:

```bash
curl -fsS http://127.0.0.1:3000/healthz
curl -fsS http://127.0.0.1:8000/healthz
```

Expected responses:
- Frontend: `{"status":"ok"}`
- API: `{"status":"ok"}`

Submit and track a sample job:

```bash
JOB_ID=$(curl -fsS -X POST http://127.0.0.1:3000/submit | python -c "import json,sys; print(json.load(sys.stdin)['job_id'])")
curl -fsS "http://127.0.0.1:3000/status/${JOB_ID}"
```

Expected:
- A valid `job_id` is returned
- Job status transitions to `completed`

## 5. Run integration test script

```bash
bash scripts/integration_test.sh .env
```

Expected output includes:
- `Integration test passed: job completed`

## 6. Stop and clean up

```bash
docker compose --env-file .env -f docker-compose.yml down -v --remove-orphans
```

## Security and Submission Notes

- `.env` is ignored and must never be committed.
- Use `.env.example` for required variable documentation.
- Do not hardcode secrets, passwords, or tokens in source files, YAML, scripts, or history.
- Keep repository public for grading.
- Commit all work; do not leave required changes only in local workspace.
- Do not open a pull request to the starter repository.
