# FIXES

This document lists bugs/issues addressed in this update, including file, line number(s), what was wrong, and the fix applied.

| File | Line(s) | Bug / Issue | Fix Applied |
| --- | ---: | --- | --- |
| `api/.env` (deleted) | 1-2 | Sensitive values were committed (`REDIS_PASSWORD`, production env marker). | Removed tracked file and moved env-driven config to `.env.example` + `.gitignore` protection. |
| `.gitignore` | 1-3 | `.env` files were not consistently ignored, risking accidental secret commits. | Added `.env`, `*.env`, and `**/.env` ignore rules. |
| `.env.example` | 2-31 | Required runtime variables were not fully documented in a shareable template. | Added placeholders/defaults for all required variables used by compose/services. |
| `api/main.py` | 8-13, 26 | Redis host/port/queue were effectively hardwired for local-only assumptions. | Switched to env-based `REDIS_HOST`, `REDIS_PORT`, and `QUEUE_NAME`; enabled `decode_responses=True`. |
| `api/main.py` | 15-21 | API had no container health endpoint and no Redis readiness signal. | Added `/healthz` with Redis ping and `503` on Redis failures. |
| `api/main.py` | 35 | Status response tried to decode bytes manually; brittle with different Redis client modes. | Returned decoded string directly by enabling `decode_responses=True`. |
| `worker/worker.py` | 6-13, 32 | Worker queue/Redis settings were not configurable and assumed localhost. | Added env-driven Redis and queue settings with configurable poll timeout. |
| `worker/worker.py` | 16-23, 31 | Worker had no graceful termination path for container stop signals. | Added SIGINT/SIGTERM handlers and loop guard via `RUNNING` flag. |
| `worker/worker.py` | 26 | Processing delay was hardcoded. | Made delay configurable via `PROCESSING_DELAY_SECONDS`. |
| `frontend/app.js` | 6-7 | Frontend API target and port were static, causing breakage in containerized envs. | Added `API_BASE_URL` and `FRONTEND_PORT` env-driven configuration. |
| `frontend/app.js` | 30-32 | No app-level health endpoint for orchestration checks. | Added `/healthz` endpoint returning service status. |
| `compose.yaml` | 2-67 | Previous compose topology did not represent the actual stack and had weak orchestration semantics. | Replaced with Redis/API/worker/frontend stack, env wiring, health-gated `depends_on`, and resource limits. |
| `docker-compose.yml` | 1-71 | Some tooling expects classic filename; missing compatibility compose file could break CI/dev scripts. | Added equivalent `docker-compose.yml` for compatibility with explicit `-f` usage. |
| `api/Dockerfile` | 1-30 | Used older base image and runtime model without least-privilege user or healthcheck. | Upgraded to Python 3.11 multi-stage, venv copy, non-root user, and HTTP healthcheck. |
| `worker/Dockerfile` | 1-29 | Similar container hardening/performance gaps as API image. | Upgraded to Python 3.11 multi-stage, non-root user, and Redis ping healthcheck. |
| `frontend/Dockerfile` | 1-24 | Outdated Node image and missing runtime hardening/healthcheck. | Upgraded to Node 22 multi-stage install, non-root user, and HTTP healthcheck. |
| `frontend/package.json` | 5-17 | Frontend lacked lint script and lint dependencies for CI checks. | Added `lint` script plus `eslint`, `@eslint/js`, and `globals` dev dependencies. |
| `frontend/eslint.config.mjs` | 1-22 | No ESLint config for modern Node/CommonJS checks. | Added ESLint flat config with Node globals and baseline rules. |
| `api/requirements-dev.txt` | 1-4 | Missing explicit dev/test dependency set for consistent local/CI validation. | Added `pytest`, `pytest-cov`, `flake8`, and `httpx`. |
| `api/tests/test_main.py` | 1-73 | API lacked isolated tests for queueing/status and health endpoint behavior. | Added unit tests using `FakeRedis` and monkeypatch for deterministic behavior. |
| `.github/workflows/ci-cd.yml` | 35-158 | Pipeline lacked complete staged validation and deployment flow for this stack. | Added staged lint, unit test+coverage, image build/push, Trivy scan, integration test, and main-only rolling deploy. |
| `scripts/integration_test.sh` | 1-46 | No reusable smoke/integration script to validate end-to-end job processing. | Added health wait, job submission, and completion polling checks with strict exit codes. |
| `scripts/rolling_update.sh` | 1-39 | No safe rolling replacement procedure for frontend container. | Added candidate container health gating, conditional old-container swap, and rollback-on-failure path. |
