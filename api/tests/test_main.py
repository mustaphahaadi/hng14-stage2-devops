from fastapi.testclient import TestClient

import main


class FakeRedis:
    def __init__(self):
        self.queue = []
        self.hashes = {}

    def lpush(self, key, value):
        self.queue.insert(0, (key, value))

    def hset(self, key, field, value):
        if key not in self.hashes:
            self.hashes[key] = {}
        self.hashes[key][field] = value

    def hget(self, key, field):
        return self.hashes.get(key, {}).get(field)

    def ping(self):
        return True


def test_create_job_queues_job_and_sets_status(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(main, 'r', fake)
    monkeypatch.setattr(main, 'QUEUE_NAME', 'job')

    client = TestClient(main.app)
    response = client.post('/jobs')

    assert response.status_code == 200
    payload = response.json()
    job_id = payload['job_id']

    assert fake.queue[0] == ('job', job_id)
    assert fake.hashes[f'job:{job_id}']['status'] == 'queued'


def test_get_job_returns_not_found_when_missing(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(main, 'r', fake)

    client = TestClient(main.app)
    response = client.get('/jobs/does-not-exist')

    assert response.status_code == 200
    assert response.json() == {'error': 'not found'}


def test_get_job_returns_status_when_found(monkeypatch):
    fake = FakeRedis()
    fake.hset('job:abc123', 'status', 'completed')
    monkeypatch.setattr(main, 'r', fake)

    client = TestClient(main.app)
    response = client.get('/jobs/abc123')

    assert response.status_code == 200
    assert response.json() == {'job_id': 'abc123', 'status': 'completed'}


def test_healthz_returns_ok_when_redis_ping_works(monkeypatch):
    fake = FakeRedis()
    monkeypatch.setattr(main, 'r', fake)

    client = TestClient(main.app)
    response = client.get('/healthz')

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
