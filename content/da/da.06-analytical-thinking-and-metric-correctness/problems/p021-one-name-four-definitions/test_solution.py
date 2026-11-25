import pandas as pd
import pytest

from solution import completed_in_february


def jobs():
    rows = [
        # id, created_at,            started_at,           completed_at,         status       why this row exists
        (1, "2025-01-31 12:00:00", "2025-02-02 08:00:00", "2025-02-03 08:00:00", "completed"),   # created in January, done in February
        (2, "2025-02-01 00:00:00", "2025-02-04 08:00:00", "2025-02-05 08:00:00", "completed"),   # created exactly at the start of February
        (3, "2025-02-10 09:00:00", "2025-02-11 08:00:00", "2025-02-28 20:00:00", "completed"),   # 20:00 UTC on the 28th is 01:30 IST on 1 March
        (4, "2025-02-12 09:00:00", None,                  None,                  "cancelled"),   # never started
        (5, "2025-02-20 09:00:00", "2025-02-21 08:00:00", None,                  "pending"),     # started, not finished
        (6, "2025-02-25 09:00:00", "2025-03-01 00:00:00", "2025-03-02 08:00:00", "completed"),   # started exactly at the end of February
        (7, "2025-02-27 09:00:00", "2025-02-28 08:00:00", "2025-03-01 00:00:00", "completed"),   # completed exactly at the end (UTC)
        (8, "2025-01-31 20:00:00", "2025-01-31 22:00:00", "2025-01-31 23:00:00", "completed"),   # 23:00 UTC on 31 Jan is 04:30 IST on 1 Feb
        (9, "2025-02-26 09:00:00", "2025-02-28 20:00:00", "2025-02-28 23:00:00", "completed"),   # 23:00 UTC on the 28th is 04:30 IST on 1 March
    ]
    df = pd.DataFrame(rows, columns=["job_id", "created_at", "started_at", "completed_at", "status"])
    for c in ("created_at", "started_at", "completed_at"):
        df[c] = pd.to_datetime(df[c])
    return df


def test_by_created():
    got = completed_in_february(jobs(), "by_created")
    assert got == 7, ("created in February (>= Feb 1 00:00, < Mar 1 00:00), any status: jobs 2, 3, 4, 5, 6, 7, 9 = 7. "
                      "Job 2 is created exactly at the start and counts. Got %s." % got)


def test_by_started():
    got = completed_in_february(jobs(), "by_started")
    assert got == 6, ("started in February: jobs 1, 2, 3, 5, 7, 9 = 6. Job 6 starts exactly at the end of February: March. "
                      "Job 4 never started. Got %s." % got)


def test_by_completed():
    got = completed_in_february(jobs(), "by_completed")
    assert got == 4, ("status completed AND completed_at in February (UTC): jobs 1, 2, 3, 9 = 4. Job 7 completes exactly at the "
                      "end (March); job 6 in March; job 8 in January. Got %s." % got)


def test_by_completed_ist_shifts_the_clock_by_five_and_a_half_hours():
    got = completed_in_february(jobs(), "by_completed_ist")
    assert got == 3, ("in IST (UTC + 5:30): job 8 moves INTO February (04:30 on 1 Feb), jobs 3, 7 and 9 move OUT (they "
                      "complete after 00:00 IST on 1 March). February jobs: 1, 2, 8 = 3. Got %s." % got)


def test_the_four_definitions_give_four_different_numbers():
    j = jobs()
    counts = {d: completed_in_february(j, d) for d in ("by_created", "by_started", "by_completed", "by_completed_ist")}
    assert sorted(counts.values()) == [3, 4, 6, 7], (
        "four definitions of 'February jobs' give different numbers: %s." % counts)


def test_unknown_definition_raises():
    with pytest.raises(ValueError, match="by_foo"):
        completed_in_february(jobs(), "by_foo")


def test_returns_plain_int_and_leaves_jobs_alone():
    j = jobs()
    before = j.copy()
    assert type(completed_in_february(j, "by_created")) is int, "return a plain int."
    pd.testing.assert_frame_equal(j, before)
    assert j["completed_at"].dt.tz is None, "do not change the time zone of the input: compute the shifted clock on a copy."
