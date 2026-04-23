FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /build
COPY requirements.txt ./
RUN python -m venv /opt/venv \
	&& /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PATH="/opt/venv/bin:$PATH"

RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
COPY . .

RUN chown -R appuser:appgroup /app
USER appuser

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=5 \
  CMD python -c "import os, redis; r=redis.Redis(host=os.getenv('REDIS_HOST','redis'), port=int(os.getenv('REDIS_PORT','6379'))); r.ping()"

CMD ["python", "worker.py"]