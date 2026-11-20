import threading
from collections import Counter

from solution import complete, heartbeat, reserve


def test_reserve_claims(connect, add_jobs):
    add_jobs(2)
    db = connect()
    job = reserve(db, "worker-A", now=0, lease=30)
    assert job is not None, "A queued job with run_at <= now must be reserved."
    assert (job["id"], job["state"], job["attempts"], job["worker"], job["lease_until"]) == (1, "running", 1, "worker-A", 30), \
        f"Return the row AFTER the update (id 1, running, attempts 1, worker-A, lease_until 30); got {dict(job)}"
    assert reserve(db, "worker-A", now=0)["id"] == 2, "The next reserve takes the next job."
    assert reserve(db, "worker-A", now=0) is None, "Nothing left: None."


def test_crash_and_lease(connect, add_jobs):
    add_jobs(1)
    a, b = connect(), connect()
    mine = reserve(a, "worker-A", now=0, lease=30)
    assert reserve(b, "worker-B", now=10) is None, "While A's lease lasts nobody else may take the job."
    taken = reserve(b, "worker-B", now=30, lease=30)
    assert taken is not None and taken["id"] == mine["id"], \
        "When lease_until <= now the job is ready again (its worker probably crashed)."
    assert taken["attempts"] == 2 and taken["worker"] == "worker-B"
    assert complete(a, mine["id"], "worker-A", now=31) is False, \
        "A's late complete must be refused: check `worker = ?` AND `state = 'running'` and return rowcount == 1."
    assert complete(b, taken["id"], "worker-B", now=32) is True
    assert complete(b, taken["id"], "worker-B", now=33) is False, "A job that is already done cannot be completed again."


def test_done_jobs_stay_done(connect, add_jobs):
    add_jobs(1)
    db = connect()
    job = reserve(db, "w", now=0, lease=10)
    complete(db, job["id"], "w", now=1)
    assert reserve(db, "w", now=1000) is None, "A done job must never be reserved again (lease_until is cleared / state is done)."


def test_heartbeat(connect, add_jobs):
    add_jobs(1)
    a, b = connect(), connect()
    job = reserve(a, "worker-A", now=0, lease=30)
    assert heartbeat(a, job["id"], "worker-A", now=25, lease=30) is True, "The holder extends its lease."
    assert reserve(b, "worker-B", now=40) is None, "After the heartbeat at t=25 the lease lasts until 55."
    assert heartbeat(b, job["id"], "worker-B", now=41) is False, "Only the holder may extend the lease."
    taken = reserve(b, "worker-B", now=55)
    assert taken is not None, "Without another heartbeat the lease ends at 55."
    assert heartbeat(a, job["id"], "worker-A", now=56) is False, "A lost the job: heartbeat must say False so A stops."


def test_order_by_run_at_then_id(connect, db_path):
    import sqlite3
    with sqlite3.connect(db_path, isolation_level=None) as raw:
        raw.execute("INSERT INTO jobs (kind, run_at) VALUES ('late', 5)")
        raw.execute("INSERT INTO jobs (kind, run_at) VALUES ('early', 1)")
        raw.execute("INSERT INTO jobs (kind, run_at) VALUES ('future', 100)")
    db = connect()
    assert reserve(db, "w", now=10)["kind"] == "early", "The job with the smallest run_at goes first."
    assert reserve(db, "w", now=10)["kind"] == "late"
    assert reserve(db, "w", now=10) is None, "A job whose run_at is in the future is not ready."


def _drain(connections, now_lease=60):
    claimed, lock = [], threading.Lock()
    gate = threading.Barrier(len(connections))

    def worker(name, db):
        gate.wait()
        while True:
            job = reserve(db, name, now=0, lease=now_lease)
            if job is None:
                return
            with lock:
                claimed.append((job["id"], name))
            complete(db, job["id"], name, now=0)

    threads = [threading.Thread(target=worker, args=(f"w{i}", db)) for i, db in enumerate(connections)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=40)
    return claimed


def test_four_workers_no_double_claims(connect, add_jobs):
    add_jobs(200)
    claimed = _drain([connect() for _ in range(4)])
    per_job = Counter(job_id for job_id, _ in claimed)
    twice = [j for j, n in per_job.items() if n > 1]
    assert not twice, f"Jobs claimed twice: {twice[:5]}. Find and claim the job in ONE statement."
    assert len(per_job) == 200, f"All 200 jobs must be claimed exactly once; claimed {len(per_job)}."


def test_no_double_claims_when_select_is_slow(connect, add_jobs):
    add_jobs(30)
    claimed = _drain([connect(slow=True) for _ in range(4)])
    per_job = Counter(job_id for job_id, _ in claimed)
    twice = sorted(j for j, n in per_job.items() if n > 1)
    assert not twice, \
        f"With slow SELECTs, jobs {twice[:5]} were claimed by two workers. SELECT-then-UPDATE is two steps: " \
        "use UPDATE ... WHERE id = (SELECT ...) RETURNING *, or UPDATE ... WHERE id = ? AND <still claimable> and check rowcount."
    assert len(per_job) == 30, f"All 30 jobs must be claimed; claimed {len(per_job)}."
