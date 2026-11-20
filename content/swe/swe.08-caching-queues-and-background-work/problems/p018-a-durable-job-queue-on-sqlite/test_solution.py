import json
import sqlite3

from solution import JobQueue


def test_enqueue_returns_ids_and_stores_json(db_path, clock):
    q = JobQueue(db_path, now=clock)
    a = q.enqueue("email", {"to": "ada", "n": 1})
    b = q.enqueue("email", {"to": "bo"})
    assert (a, b) == (1, 2), f"enqueue returns the new job id: expected 1 then 2, got {(a, b)}"
    job = q.get(a)
    assert job is not None, "get(job_id) must return the row as a dict."
    assert json.loads(job["payload"]) == {"to": "ada", "n": 1}, "Store the payload as JSON text."
    assert job["payload"] == json.dumps({"to": "ada", "n": 1}, sort_keys=True), "Use json.dumps(payload, sort_keys=True)."
    assert (job["state"], job["attempts"], job["run_at"], job["created_at"]) == ("queued", 0, 1000.0, 1000.0), \
        f"A new job is queued, 0 attempts, run_at = created_at = now; got {(job['state'], job['attempts'], job['run_at'], job['created_at'])}"


def test_survives_a_restart(db_path, clock):
    JobQueue(db_path, now=clock).enqueue("email", {"to": "ada"})
    again = JobQueue(db_path, now=clock)                 # a new process opens the same file
    job = again.reserve("w1")
    assert job is not None and json.loads(job["payload"]) == {"to": "ada"}, \
        "Jobs live in the SQLite file: a new JobQueue on the same path must see them. Did you use :memory: or forget CREATE TABLE IF NOT EXISTS?"


def test_reserve_order_and_delay(db_path, clock):
    q = JobQueue(db_path, now=clock)
    q.enqueue("email", {"to": "ada"})
    q.enqueue("email", {"to": "bo"}, delay=60)
    q.enqueue("email", {"to": "cy"})
    order = []
    for _ in range(2):
        job = q.reserve("w1")
        order.append(json.loads(job["payload"])["to"])
        q.complete(job["id"], "w1")
    assert order == ["ada", "cy"], f"Oldest ready job first; bo is delayed by 60 s. Got {order}"
    assert q.reserve("w1") is None, "bo's run_at is in the future: nothing is ready, so reserve returns None."
    clock.advance(60)
    job = q.reserve("w1")
    assert job is not None and json.loads(job["payload"])["to"] == "bo", "After 60 s the delayed job is ready."


def test_reserve_claims_the_row(db_path, clock):
    q = JobQueue(db_path, now=clock)
    jid = q.enqueue("report", {})
    job = q.reserve("worker-A", lease=30)
    assert job["id"] == jid and job["state"] == "running", "reserve returns the row AFTER the update: state 'running'."
    assert job["attempts"] == 1, "reserve counts an attempt (attempts + 1)."
    assert job["worker"] == "worker-A" and job["lease_until"] == 1030.0, "Store who holds the job and lease_until = now + lease."
    assert q.reserve("worker-B") is None, "A leased job is not given to anyone else while the lease lasts."


def test_expired_lease_gives_the_job_back(db_path, clock):
    q = JobQueue(db_path, now=clock)
    q.enqueue("report", {})
    mine = q.reserve("worker-A", lease=30)
    clock.advance(30)
    taken = q.reserve("worker-B", lease=30)
    assert taken is not None and taken["id"] == mine["id"], \
        "When lease_until <= now, the running job is ready again (its worker probably died)."
    assert taken["attempts"] == 2 and taken["worker"] == "worker-B"
    assert q.complete(mine["id"], "worker-A") is False, "A's late complete must be refused: B holds the lease now."
    assert q.complete(taken["id"], "worker-B") is True
    assert q.get(taken["id"])["state"] == "done"


def test_complete_rules(db_path, clock):
    q = JobQueue(db_path, now=clock)
    jid = q.enqueue("x", {})
    q.reserve("w1")
    clock.advance(5)
    assert q.complete(jid, "w1") is True
    job = q.get(jid)
    assert (job["state"], job["finished_at"], job["lease_until"]) == ("done", 1005.0, None), \
        "complete sets state 'done', finished_at = now and clears lease_until."
    assert q.complete(jid, "w1") is False, "Completing a job that is not running any more returns False."
    assert q.reserve("w1") is None, "A done job never comes back."


def test_dedupe_key(db_path, clock):
    q = JobQueue(db_path, now=clock)
    a = q.enqueue("invoice", {"order": 7}, dedupe_key="invoice:order-7")
    b = q.enqueue("invoice", {"order": 7}, dedupe_key="invoice:order-7")
    c = q.enqueue("invoice", {"order": 8}, dedupe_key="invoice:order-8")
    assert a == b, "The same dedupe key must return the SAME job id, not create a second job."
    assert c != a
    with sqlite3.connect(db_path) as db:
        n = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    assert n == 2, f"Two distinct dedupe keys = 2 jobs, got {n}."
    q.enqueue("x", {})
    q.enqueue("x", {})
    with sqlite3.connect(db_path) as db:
        n = db.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    assert n == 4, "Jobs WITHOUT a dedupe key are never merged (NULL is not equal to NULL in a UNIQUE column)."


def test_fail_retry_later(db_path, clock):
    q = JobQueue(db_path, now=clock)
    jid = q.enqueue("x", {}, max_attempts=3)
    job = q.reserve("w1")
    assert q.fail(job, "ConnectionError: timeout", retry_in=10) is True
    row = q.get(jid)
    assert (row["state"], row["run_at"], row["last_error"], row["lease_until"]) == ("queued", 1010.0, "ConnectionError: timeout", None), \
        f"A retryable failure puts the job back: queued, run_at = now + retry_in, last_error stored; got {row}"
    assert q.reserve("w1") is None, "Not before run_at."
    clock.advance(10)
    assert q.reserve("w1")["attempts"] == 2


def test_fail_until_dead(db_path, clock):
    q = JobQueue(db_path, now=clock)
    jid = q.enqueue("x", {}, max_attempts=2)
    for _ in range(2):
        job = q.reserve("w1")
        q.fail(job, "boom")
    row = q.get(jid)
    assert row["state"] == "dead" and row["attempts"] == 2 and row["last_error"] == "boom", \
        f"After max_attempts failures the job is dead with the last error; got {(row['state'], row['attempts'], row['last_error'])}"
    assert row["finished_at"] == 1000.0
    assert q.reserve("w1") is None, "A dead job is never reserved again."


def test_permanent_failure(db_path, clock):
    q = JobQueue(db_path, now=clock)
    jid = q.enqueue("x", {}, max_attempts=5)
    job = q.reserve("w1")
    q.fail(job, "permanent: bad payload", permanent=True)
    assert q.get(jid)["state"] == "dead", "permanent=True buries the job at once, even with attempts left."


def test_fail_by_stale_worker_is_refused(db_path, clock):
    q = JobQueue(db_path, now=clock)
    jid = q.enqueue("x", {})
    old = q.reserve("worker-A", lease=30)
    clock.advance(31)
    q.reserve("worker-B", lease=30)
    assert q.fail(old, "late error", retry_in=5) is False, "fail() from a worker that lost the lease must change nothing."
    assert q.get(jid)["worker"] == "worker-B" and q.get(jid)["state"] == "running"


def test_get_missing(db_path, clock):
    assert JobQueue(db_path, now=clock).get(99) is None, "get() of an unknown id returns None."
