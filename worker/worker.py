import redis
import time
import os
import signal

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
QUEUE_NAME = os.getenv("QUEUE_NAME", "job")
POLL_TIMEOUT_SECONDS = int(os.getenv("POLL_TIMEOUT_SECONDS", "5"))
PROCESSING_DELAY_SECONDS = int(os.getenv("PROCESSING_DELAY_SECONDS", "2"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
RUNNING = True


def _handle_shutdown(_signum, _frame):
    global RUNNING
    RUNNING = False


signal.signal(signal.SIGINT, _handle_shutdown)
signal.signal(signal.SIGTERM, _handle_shutdown)

def process_job(job_id):
    print(f"Processing job {job_id}")
    time.sleep(PROCESSING_DELAY_SECONDS)  # simulate work
    r.hset(f"job:{job_id}", "status", "completed")
    print(f"Done: {job_id}")


while RUNNING:
    job = r.brpop(QUEUE_NAME, timeout=POLL_TIMEOUT_SECONDS)
    if job:
        _, job_id = job
        process_job(job_id)