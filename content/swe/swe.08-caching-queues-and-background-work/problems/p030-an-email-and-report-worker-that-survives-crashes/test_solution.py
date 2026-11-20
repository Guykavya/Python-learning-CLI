import hashlib
import os

import pytest
from fastapi.testclient import TestClient

from solution import create_app

EXPECTED = b"month,order_id,customer,total_cents\n2026-10,1,ada,2500\n2026-10,2,bo,4200\n2026-10,3,cy,990\n"
CRASH_POINTS = ["report:mid-write", "report:before-replace", "report:after-replace", "report:after-status",
                "email:after-claim", "email:after-send", "email:after-record"]


def request(world, month="2026-10"):
    return TestClient(create_app(world.queue)).post("/reports", json={"month": month})


def report_file(world, month="2026-10"):
    path = os.path.join(world.out_dir, f"report-{month}.csv")
    with open(path, "rb") as f:
        return f.read()


def assert_final_state(world, label):
    assert len(world.provider.outbox) == 1, \
        f"[{label}] finance must receive exactly ONE e-mail, got {len(world.provider.outbox)}. " \
        "Use the log + idempotency key of p022, and enqueue the e-mail job with a dedupe key."
    assert report_file(world) == EXPECTED, f"[{label}] the report file must be complete and identical to a clean run."
    status = TestClient(create_app(world.queue)).get("/reports/2026-10").json()
    assert status == {"month": "2026-10", "status": "ready", "digest": hashlib.sha256(EXPECTED).hexdigest()[:12]}, \
        f"[{label}] GET /reports/2026-10 must say ready with the first 12 hex characters of the file's SHA-256; got {status}"
    assert world.job_states() == {("report", "done"), ("report_email", "done")}, \
        f"[{label}] every job must end done; got {sorted(world.job_states())}"


# ---------------------------------------------------------------- the API
def test_post_accepts_and_queues(make_world):
    world = make_world()
    r = request(world)
    assert r.status_code == 202, f"POST /reports answers 202 Accepted at once; got {r.status_code}"
    assert r.json() == {"month": "2026-10", "status": "queued", "status_url": "/reports/2026-10"}, r.json()
    jobs = world.jobs()
    assert [(j["kind"], j["dedupe_key"]) for j in jobs] == [("report", "report:2026-10")], \
        f"One report job with dedupe_key 'report:<month>'; got {[(j['kind'], j['dedupe_key']) for j in jobs]}"


def test_post_twice_makes_one_job(make_world):
    world = make_world()
    request(world)
    second = request(world)
    assert second.status_code == 202
    assert len(world.jobs()) == 1, "Asking for the same month twice must create ONE job (the dedupe key is the month)."


def test_invalid_month_refused_at_the_door(make_world):
    world = make_world()
    for bad in ("2026-13", "2026-1", "october", ""):
        assert request(world, bad).status_code == 422, f"{bad!r} is not a month: 422, and no job."
    assert world.jobs() == []


def test_get_status(make_world):
    world = make_world()
    client = TestClient(create_app(world.queue))
    assert client.get("/reports/2026-10").status_code == 404, "An unknown report: 404."
    assert client.get("/reports/26-10").status_code == 422, "A malformed month in the URL: 422."
    request(world)
    assert client.get("/reports/2026-10").json() == {"month": "2026-10", "status": "queued", "digest": None}


# ---------------------------------------------------------------- the worker
def test_clean_run(make_world):
    world = make_world()
    request(world)
    world.run()
    assert_final_state(world, "no crash")
    assert world.provider.outbox[0]["to"] == "finance@example.com"
    assert world.provider.outbox[0]["subject"] == "Your report for 2026-10 is ready"
    jobs = world.jobs()
    assert [(j["kind"], j["dedupe_key"]) for j in jobs] == [("report", "report:2026-10"), ("report_email", "report-email:2026-10")], \
        "The report handler enqueues one 'report_email' job with dedupe_key 'report-email:<month>'."


@pytest.mark.parametrize("point", CRASH_POINTS)
def test_kill_it_everywhere(make_world, point):
    world = make_world()
    request(world)
    world.run(crash_point=point)
    assert_final_state(world, f"crash at {point}")


def test_crash_mid_write_never_shows_half_a_file(make_world):
    world = make_world()
    request(world)
    first = world.handlers("report:mid-write")
    from_queue = world.queue.reserve("w")
    try:
        first["report"]({"month": "2026-10"}, from_queue)
    except BaseException:
        pass
    assert not os.path.exists(os.path.join(world.out_dir, "report-2026-10.csv")), \
        "After a crash in the middle of writing, the final file name must not exist yet (write a .tmp file, then os.replace)."


def test_duplicate_deliveries(make_world):
    world = make_world()
    request(world)
    world.run()
    world.queue.enqueue("report", {"month": "2026-10"})           # a duplicate report job (no dedupe key)
    world.queue.enqueue("report_email", {"month": "2026-10"})     # a duplicate e-mail job
    world.run()
    assert len(world.provider.outbox) == 1, "Duplicate report and e-mail jobs must not send a second e-mail."
    assert report_file(world) == EXPECTED, "Rebuilding the report gives identical bytes."
    assert {s for _, s in world.job_states()} == {"done"}


def test_outage_dead_letters_then_redrive(make_world):
    world = make_world()
    request(world)
    world.provider.down = True
    world.run(recovery_rounds=8, step=1000)
    email_jobs = [j for j in world.jobs() if j["kind"] == "report_email"]
    assert len(email_jobs) == 1 and email_jobs[0]["state"] == "dead", \
        f"With the provider down, the e-mail job must retry and end dead after 5 attempts; got {[(j['state'], j['attempts']) for j in email_jobs]}"
    assert "ProviderTimeout" in (email_jobs[0]["last_error"] or ""), "The dead job keeps the last error (ProviderTimeout ...)."
    assert world.provider.outbox == []
    world.provider.down = False
    assert world.queue.requeue_dead(email_jobs[0]["id"]), "The operator redrives the dead job."
    world.run()
    assert_final_state(world, "outage, then redrive")


def test_bad_job_does_not_block_others(make_world):
    world = make_world()
    bad = world.queue.enqueue("report", {"month": "2026-13"})
    request(world)
    world.run()
    job = world.queue.get(bad)
    assert job["state"] == "dead" and job["attempts"] == 1, \
        "An invalid month is a PERMANENT error: raise permanent_error(...) so the job is dead at once, not retried."
    assert len(world.provider.outbox) == 1 and report_file(world) == EXPECTED, "The good report still completes."
