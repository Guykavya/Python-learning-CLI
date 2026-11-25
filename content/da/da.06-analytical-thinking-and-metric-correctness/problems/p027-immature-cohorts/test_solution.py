import pandas as pd
import pytest

from solution import mature_completion_rate

CUT = "2025-04-05 00:00:00"

# (job_id, created_at, status, why the row exists)
ROWS = [
    (1, "2025-03-01 10:00:00", "completed", "old and finished"),
    (2, "2025-03-05 10:00:00", "completed", "old and finished"),
    (3, "2025-03-10 08:00:00", "cancelled", "old, decided, not completed"),
    (4, "2025-03-22 00:00:00", "completed", "exactly 14 days old at the cut: mature (boundary)"),
    (5, "2025-03-22 00:00:01", "pending", "one second younger than 14 days: NOT mature"),
    (6, "2025-03-30 12:00:00", "pending", "young and still pending"),
    (7, "2025-04-03 09:00:00", "completed", "very young but already completed (counts in the naive rate)"),
    (8, "2025-04-05 00:00:00", "pending", "created exactly at the cut: not part of the data yet"),
    (9, "2025-04-06 00:00:00", "pending", "created after the cut: not part of the data"),
]


def jobs():
    d = pd.DataFrame([r[:3] for r in ROWS], columns=["job_id", "created_at", "status"])
    d["created_at"] = pd.to_datetime(d["created_at"])
    return d


def test_naive_and_mature_rates():
    got = mature_completion_rate(jobs(), CUT, 14)
    # jobs created before the cut: 1..7 -> 7 jobs, completed: 1, 2, 4, 7 -> 4/7. Mature (created <= 22 Mar 00:00): 1, 2, 3, 4 -> 3/4.
    assert got["jobs"] == 7, "only jobs created BEFORE the cut count (not job 8 at the cut, not job 9 after it). Got %s." % got["jobs"]
    assert got["naive"] == pytest.approx(4 / 7), "naive = completed / all 7 jobs = 4/7. Got %s." % got["naive"]
    assert got["mature_jobs"] == 4, ("mature means created_at <= cut - 14 days; job 4 is exactly 14 days old and IS mature, "
                                     "job 5 (one second younger) is not. Got %s." % got["mature_jobs"])
    assert got["mature"] == pytest.approx(3 / 4), "mature rate = completed among jobs 1-4 = 3/4. Got %s." % got["mature"]
    assert got["mature"] > got["naive"], "the naive rate is lower because young jobs are still pending."


def test_a_stricter_age_changes_the_mature_group():
    got = mature_completion_rate(jobs(), CUT, 30)
    # created <= 6 Mar 00:00: jobs 1 and 2 only, both completed
    assert (got["mature_jobs"], got["mature"]) == (2, 1.0), "with 30 days, only jobs 1 and 2 are old enough. Got %s." % got


def test_no_mature_jobs_gives_none():
    got = mature_completion_rate(jobs(), CUT, 400)
    assert got["mature_jobs"] == 0 and got["mature"] is None, "when no job is old enough the mature rate is None, not 0 and not an error."
    assert got["naive"] == pytest.approx(4 / 7), "the naive rate does not depend on the age."


def test_age_zero_makes_everyone_mature():
    got = mature_completion_rate(jobs(), CUT, 0)
    assert got["mature_jobs"] == 7 and got["mature"] == pytest.approx(got["naive"]), (
        "with min_age_days = 0 every job created before the cut is mature, so the two rates agree.")


def test_accepts_timestamp_and_text_and_keeps_input():
    d = jobs()
    a = mature_completion_rate(d, pd.Timestamp(CUT), 14)
    b = mature_completion_rate(d, CUT, 14)
    assert a == b, "cut may be a Timestamp or a date text."
    assert len(d) == 9 and d["created_at"].is_monotonic_increasing, "do not filter or change the caller's table."
