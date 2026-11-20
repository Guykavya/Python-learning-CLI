import pytest

from solution import backoff_delay, dead_letters, process_one, redrive, redrive_all

MID = lambda: 0.5           # rng that gives 0.75 x delay


class BadPayload(Exception):
    pass


class Handler:
    """Fails the first `failures` calls with `error`, then succeeds. Records the payloads it saw."""

    def __init__(self, failures=0, error=ConnectionError("provider down")):
        self.failures, self.error, self.seen = failures, error, []

    def __call__(self, payload):
        self.seen.append(payload)
        if len(self.seen) <= self.failures:
            raise self.error


def test_backoff_table():
    lows = [backoff_delay(a, rng=lambda: 0.0) for a in range(1, 10)]
    highs = [backoff_delay(a, rng=lambda: 1.0) for a in range(1, 10)]
    assert lows == [1, 2, 4, 8, 16, 32, 64, 128, 150], f"Lowest delays (rng=0) must be half of min(cap, 2 * 2**(a-1)); got {lows}"
    assert highs == [2, 4, 8, 16, 32, 64, 128, 256, 300], f"Highest delays (rng=1) reach the cap of 300; got {highs}"


def test_backoff_custom():
    assert backoff_delay(3, base=10, cap=1000, rng=MID) == pytest.approx(30), "attempt 3, base 10: delay 40, 0.75 x 40 = 30."


def test_nothing_to_do(queue):
    assert process_one(queue, Handler(), "w1") is None, "An empty queue gives None."


def test_success_and_payload(queue):
    h = Handler()
    jid = queue.enqueue("email", {"to": "ada"})
    assert process_one(queue, h, "w1") == "done"
    assert h.seen == [{"to": "ada"}], "The handler gets the payload as a dict (json.loads of the stored text)."
    assert queue.get(jid)["state"] == "done"


def test_retry_with_backoff(queue, clock):
    jid = queue.enqueue("email", {"to": "ada"})
    assert process_one(queue, Handler(failures=9), "w1", rng=MID) == "retry"
    job = queue.get(jid)
    assert job["state"] == "queued" and job["run_at"] == pytest.approx(1.5), \
        f"Attempt 1 failed: retry at now + backoff_delay(1) = 1.5; got {job['state']}, run_at={job['run_at']}"
    assert job["last_error"] == "ConnectionError: provider down", "last_error is 'TypeName: message'."


def test_until_dead(queue, clock):
    jid = queue.enqueue("email", {}, max_attempts=3)
    h = Handler(failures=99)
    outcomes = []
    for _ in range(3):
        outcomes.append(process_one(queue, h, "w1", rng=MID))
        clock.advance(100)
    assert outcomes == ["retry", "retry", "dead"], f"Three attempts allowed: retry, retry, dead; got {outcomes}"
    assert queue.get(jid)["state"] == "dead"


def test_permanent_error_is_dead_at_once(queue):
    jid = queue.enqueue("email", {"to": "x"}, max_attempts=5)
    h = Handler(failures=1, error=BadPayload("no @ in address"))
    assert process_one(queue, h, "w1", permanent=(BadPayload,)) == "dead", \
        "An instance of a `permanent` type must bury the job at once (fail(..., permanent=True))."
    job = queue.get(jid)
    assert (job["state"], job["attempts"], job["last_error"]) == ("dead", 1, "BadPayload: no @ in address")


def test_dead_letters_inbox(queue, clock):
    queue.enqueue("ok", {})
    a = queue.enqueue("email", {}, max_attempts=1)
    b = queue.enqueue("report", {}, max_attempts=1)
    process_one(queue, Handler(), "w1")
    process_one(queue, Handler(failures=1), "w1")
    process_one(queue, Handler(failures=1, error=ValueError("bad month")), "w1")
    assert dead_letters(queue) == [
        {"id": a, "kind": "email", "attempts": 1, "last_error": "ConnectionError: provider down"},
        {"id": b, "kind": "report", "attempts": 1, "last_error": "ValueError: bad month"},
    ], "dead_letters lists dead jobs only, ordered by id, with id, kind, attempts and last_error."


def test_redrive(queue, clock):
    jid = queue.enqueue("email", {}, max_attempts=1)
    process_one(queue, Handler(failures=1), "w1")
    assert redrive(queue, jid) is True
    job = queue.get(jid)
    assert job["state"] == "queued" and job["attempts"] == 0, "Redrive resets the job to queued with 0 attempts."
    assert process_one(queue, Handler(), "w1") == "done", "After the fix, the redriven job runs and succeeds."
    assert redrive(queue, jid) is False, "A job that is not dead cannot be redriven."


def test_redrive_a_few_first(queue):
    ids = [queue.enqueue("n", {"i": i}, max_attempts=1) for i in range(5)]
    for _ in ids:
        process_one(queue, Handler(failures=1), "w1")
    assert redrive_all(queue, limit=2) == 2, "With limit=2 only two jobs are redriven."
    assert [d["id"] for d in dead_letters(queue)] == ids[2:], "The FIRST two dead jobs (by id) were redriven."
    assert redrive_all(queue) == 3, "Without a limit, all remaining dead jobs."
    assert dead_letters(queue) == []


def test_lease_lost(queue, clock):
    queue.enqueue("slow", {})

    def slow_handler(payload):
        clock.advance(31)                      # the job outlives its 30 s lease...
        queue.reserve("other-worker")          # ...and another worker takes it

    assert process_one(queue, slow_handler, "w1") == "lease-lost", \
        "When complete() returns False (another worker holds the job now), return 'lease-lost'."
