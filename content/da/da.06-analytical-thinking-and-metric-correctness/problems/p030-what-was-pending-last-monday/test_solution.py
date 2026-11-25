import pandas as pd

from solution import pending_on

COLS = ["job_id", "status", "created_at", "completed_at", "cancelled_at"]
WHEN = "2025-02-10 00:00:00"
# (row, why it exists). "today" is the extraction; WHEN is last Monday.
ROWS = [
    (1, "completed", "2025-02-01 09:00:00", "2025-02-15 09:00:00", None),   # completed AFTER when: open then, although status says completed
    (2, "completed", "2025-02-01 09:00:00", "2025-02-05 09:00:00", None),   # completed before when: not open
    (3, "cancelled", "2025-02-01 09:00:00", None, "2025-02-20 09:00:00"),   # cancelled after when: open then
    (4, "cancelled", "2025-02-01 09:00:00", None, "2025-02-03 09:00:00"),   # cancelled before when: not open
    (5, "pending", "2025-02-08 09:00:00", None, None),                      # pending today and then
    (6, "pending", "2025-02-10 00:00:01", None, None),                      # created one second after when: did not exist
    (7, "pending", "2025-02-10 00:00:00", None, None),                      # created exactly at when: existed (boundary)
    (8, "completed", "2025-02-03 09:00:00", "2025-02-10 00:00:00", None),   # completed exactly at when: already done (boundary)
    (9, "failed", "2025-02-02 09:00:00", None, None),                       # failed: no time, counted as open (upper bound)
    (10, "completed", "2025-02-09 23:00:00", "2025-02-10 00:00:01", None),  # completed one second after when: open then
]


def jobs():
    d = pd.DataFrame(ROWS, columns=COLS)
    for c in COLS[2:]:
        d[c] = pd.to_datetime(d[c])
    return d


def test_open_jobs_on_last_monday():
    got = pending_on(jobs(), WHEN)
    assert got == [1, 3, 5, 7, 9, 10], (
        "open at 10 Feb 00:00: jobs 1, 3, 10 (finished or cancelled only AFTER that moment), 5, 7 (created by then), "
        "9 (failed, counted open). Not open: 2, 4 (ended before), 8 (completed exactly at the moment: an event at 'when' has happened), "
        "6 (not created yet). Got %s" % got)


def test_today_s_status_is_not_used():
    got = pending_on(jobs(), WHEN)
    todays_pending = [r[0] for r in ROWS if r[1] == "pending"]
    assert set(todays_pending) != set(got), "a filter on today's status == 'pending' is the wrong method: it would miss jobs 1, 3, 9, 10."
    assert 1 in got and 3 in got, "jobs 1 and 3 are 'completed'/'cancelled' today but were open at the time."


def test_earlier_and_later_moments():
    assert pending_on(jobs(), "2025-01-31 00:00:00") == [], "nothing exists before the first job was created."
    early = pending_on(jobs(), "2025-02-01 09:00:00")
    assert early == [1, 2, 3, 4], "at 1 Feb 09:00 the four jobs created at that exact moment are open. Got %s." % early
    late = pending_on(jobs(), "2025-03-01 00:00:00")
    assert late == [5, 6, 7, 9], "a month later: 5, 6, 7 never ended, and failed job 9 counts as open forever. Got %s." % late


def test_input_unchanged_and_plain_ints():
    d = jobs()
    got = pending_on(d, pd.Timestamp(WHEN))
    assert all(type(j) is int for j in got), "return plain ints."
    pd.testing.assert_frame_equal(d, jobs())
