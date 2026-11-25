import pandas as pd
import pytest

from solution import completion_rates

START, END = pd.Timestamp("2025-02-01"), pd.Timestamp("2025-03-01")


def jobs():
    rows = [
        # id, created_at,            status,      started_at          why this row exists
        (1,  "2025-02-01 00:00:00", "completed", "2025-02-02"),     # created exactly at the start: included
        (2,  "2025-02-05 10:00:00", "completed", "2025-02-06"),
        (3,  "2025-02-10 09:00:00", "completed", "2025-02-11"),
        (4,  "2025-02-12 09:00:00", "cancelled", None),             # never started
        (5,  "2025-02-15 09:00:00", "failed",    "2025-02-16"),     # started, then failed
        (6,  "2025-02-20 09:00:00", "pending",   None),             # still waiting
        (7,  "2025-02-27 09:00:00", "pending",   "2025-02-28"),     # in progress
        (8,  "2025-03-01 00:00:00", "completed", "2025-03-02"),     # created exactly at the end: excluded
        (9,  "2025-01-31 23:59:59", "completed", "2025-02-02"),     # one second before the start: excluded
        (10, "2025-02-22 09:00:00", "cancelled", None),             # second cancelled job
    ]
    df = pd.DataFrame(rows, columns=["job_id", "created_at", "status", "started_at"])
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["started_at"] = pd.to_datetime(df["started_at"])
    return df


def test_cohort_is_half_open():
    got = completion_rates(jobs(), START, END)
    assert got["completed_per_created"] == pytest.approx(3 / 8), (
        "8 jobs were created in February (ids 1-7 and 10; job 8 is created AT the end and belongs to March, job 9 to January): "
        "3 completed / 8 = 0.375. Got %s." % got["completed_per_created"])


def test_completed_per_started():
    got = completion_rates(jobs(), START, END)
    assert got["completed_per_started"] == pytest.approx(3 / 5), (
        "5 February jobs have a started_at (ids 1, 2, 3, 5, 7): 3 / 5 = 0.6. Got %s." % got["completed_per_started"])


def test_completed_per_decided():
    got = completion_rates(jobs(), START, END)
    assert got["completed_per_decided"] == pytest.approx(3 / 6), (
        "'decided' = completed + cancelled + failed = 3 + 2 + 1 = 6 (pending jobs have no outcome yet): 3 / 6 = 0.5. "
        "Got %s." % got["completed_per_decided"])


def test_the_three_rates_differ():
    got = completion_rates(jobs(), START, END)
    assert len({round(v, 6) for v in got.values()}) == 3, "the three definitions give three different numbers here: %s." % got


def test_exact_keys():
    assert sorted(completion_rates(jobs(), START, END)) == ["completed_per_created", "completed_per_decided", "completed_per_started"], (
        "the dict has exactly the keys completed_per_created, completed_per_started, completed_per_decided.")


def test_accepts_date_strings():
    got = completion_rates(jobs(), "2025-02-01", "2025-03-01")
    assert got["completed_per_created"] == pytest.approx(3 / 8), "accept start/end as strings too: convert them with pd.Timestamp."


def test_empty_period_gives_none():
    got = completion_rates(jobs(), pd.Timestamp("2026-01-01"), pd.Timestamp("2026-02-01"))
    assert got == {"completed_per_created": None, "completed_per_started": None, "completed_per_decided": None}, (
        "no jobs, no rate: return None for a rate whose denominator is 0, never divide by zero. Got %s." % got)


def test_denominator_zero_only_for_that_rate():
    only_pending = jobs()[jobs()["job_id"].isin([6])]          # created in February, pending, never started
    got = completion_rates(only_pending, START, END)
    assert got["completed_per_created"] == 0.0, "1 job created, 0 completed: the rate is 0.0, not None."
    assert got["completed_per_started"] is None and got["completed_per_decided"] is None, "no started and no decided job: those two are None."


def test_frame_is_not_changed():
    j = jobs()
    before = j.copy()
    completion_rates(j, START, END)
    pd.testing.assert_frame_equal(j, before)
