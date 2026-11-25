import pandas as pd

from solution import volume_bridge

COLS = ["job_id", "status", "created_at", "started_at"]
# (job_id, status, created_at, started_at): one row per reason, each checked by hand for February 2025
ROWS = [
    (1, "completed", "2025-02-03 09:00:00", "2025-02-04 09:00:00"),   # in T and C (both)
    (2, "completed", "2025-01-30 09:00:00", "2025-02-01 00:00:00"),   # C only: created in January, started exactly at the start (boundary IN)
    (3, "cancelled", "2025-02-05 09:00:00", None),                    # T only: cancelled, never started
    (4, "failed",    "2025-02-06 09:00:00", "2025-02-07 09:00:00"),   # T only: failed (removed by the 'completed' filter)
    (5, "completed", "2025-02-28 23:00:00", "2025-03-01 00:00:00"),   # T only: started exactly at the end (boundary OUT) -> started after
    (6, "pending",   "2025-02-20 09:00:00", None),                    # T only: pending, no start date: a start filter can never select it
    (7, "pending",   "2025-01-25 09:00:00", "2025-02-10 09:00:00"),   # P only: pending but already started; created in January
    (8, "completed", "2025-03-01 00:00:00", "2025-03-02 09:00:00"),   # created exactly at the end (boundary OUT of T); in March's T and C
    (9, "completed", "2025-02-01 00:00:00", "2025-02-01 09:00:00"),   # created exactly at the start (boundary IN): T and C
]
LATE = "created before the month, started in it"


def jobs():
    d = pd.DataFrame(ROWS, columns=COLS)
    for c in ("created_at", "started_at"):
        d[c] = pd.to_datetime(d[c])
    return d


def test_the_three_sets_for_february():
    r = volume_bridge(jobs(), "2025-02-01", "2025-03-01")
    assert r["T"] == {1, 3, 4, 5, 6, 9}, (
        "T = created in [1 Feb, 1 Mar): job 9 (created exactly at the start) is in, job 8 (created exactly at the end) is out. Got %s." % sorted(r["T"]))
    assert r["C"] == {1, 2, 9}, ("C = completed AND started in the period: job 2 (started exactly at the start) is in, "
                                 "job 5 (started exactly at the end) is out, job 4 is failed. Got %s." % sorted(r["C"]))
    assert r["P"] == {7}, "P = pending AND started in the period: only job 7. Job 6 is pending but has no start date. Got %s." % sorted(r["P"])


def test_reason_labels():
    r = volume_bridge(jobs(), "2025-02-01", "2025-03-01")
    assert r["reasons"] == {
        2: LATE,
        3: "cancelled (never started)",
        4: "failed",
        5: "started after the month",
        6: "pending (no start date yet)",
    }, "every job in exactly one of T and C needs a reason (jobs 1 and 9 are in both, 7 and 8 in neither). Got %s." % r["reasons"]


def test_the_bridge_closes():
    r = volume_bridge(jobs(), "2025-02-01", "2025-03-01")
    assert r["steps"] == [
        ("created in month, cancelled (never started)", -1),
        ("created in month, failed", -1),
        ("created in month, pending (no start date yet)", -1),
        ("created in month, started after the month", -1),
        (LATE, 1),
    ], "steps: T-only labels sorted, each negative with the prefix 'created in month, ', then the +1 line last. Got %s." % r["steps"]
    assert len(r["T"]) + sum(c for _, c in r["steps"]) == len(r["C"]), "6 - 4 + 1 must equal 3."
    assert r["closes"] is True, "closes must be True when the steps reach len(C)."


def test_the_next_month_and_a_month_with_no_reasons_but_one():
    r = volume_bridge(jobs(), pd.Timestamp("2025-03-01"), pd.Timestamp("2025-04-01"))
    assert (r["T"], r["C"], r["P"]) == ({8}, {5, 8}, set()), "March: T = {8}, C = {5, 8}, P empty. Got %s." % ((r["T"], r["C"], r["P"]),)
    assert r["reasons"] == {5: LATE} and r["steps"] == [(LATE, 1)] and r["closes"], "March has one C-only job (5). Got %s." % (r,)


def test_empty_period_and_input_unchanged():
    d = jobs()
    r = volume_bridge(d, "2024-01-01", "2024-02-01")
    assert r["T"] == set() and r["C"] == set() and r["steps"] == [] and r["closes"] is True, "a period with no jobs: empty sets, no steps, closes."
    pd.testing.assert_frame_equal(d, jobs())
    assert all(type(j) is int for j in volume_bridge(d, "2025-02-01", "2025-03-01")["T"]), "ids are plain ints."


def test_a_status_filter_alone_does_not_add_up():
    r = volume_bridge(jobs(), "2025-02-01", "2025-03-01")
    assert len(r["C"]) + len(r["P"]) != len(r["T"]), "the dashboard's completed + pending is 3 + 1 = 4, not the total 6: that is the problem to explain."
