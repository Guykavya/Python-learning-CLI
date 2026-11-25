import pandas as pd

from solution import lifecycle_problems

COLS = ["job_id", "status", "created_at", "started_at", "completed_at", "cancelled_at"]
# one row per rule or per trap; the comment says why the row exists
ROWS = [
    (1, "completed", "2025-02-01 09:00", "2025-02-02 10:00", "2025-02-02 14:00", None),                 # clean
    (2, "completed", "2025-02-01 09:00", "2025-02-02 10:00", None, None),                               # completed without completed_at
    (3, "pending", "2025-02-03 09:00", None, "2025-02-05 10:00", None),                                 # completed_at on a non-completed job
    (4, "cancelled", "2025-02-03 09:00", None, None, None),                                             # cancelled without cancelled_at
    (5, "cancelled", "2025-02-03 09:00", "2025-02-04 10:00", None, "2025-02-04 12:00"),                 # cancelled but started
    (6, "completed", "2025-02-03 09:00", "2025-02-05 10:00", "2025-02-05 08:00", None),                 # completed before it started
    (7, "completed", "2025-02-03 09:00", "2025-02-03 08:00", "2025-02-03 12:00", None),                 # started before it was created
    (8, "failed", "2025-02-04 09:00", "2025-02-05 10:00", None, None),                                  # failed: no timestamp is required (clean)
    (9, "completed", "2025-02-04 09:00", "2025-02-05 10:00", "2025-02-05 10:00", None),                 # completed exactly when started: allowed (clean)
    (10, "cancelled", "2025-02-04 09:00", "2025-02-03 10:00", None, None),                              # breaks THREE rules (see test)
    (11, "failed", "2025-02-04 09:00", "2025-02-05 10:00", "2025-02-05 09:00", None),                   # non-completed with completed_at, and completed before started
]


def jobs():
    d = pd.DataFrame(ROWS, columns=COLS)
    for c in COLS[2:]:
        d[c] = pd.to_datetime(d[c])
    return d


def test_each_rule_finds_its_job():
    got = lifecycle_problems(jobs())
    want = [
        (2, "completed without completed_at"),
        (3, "completed_at on a non-completed job"),
        (4, "cancelled without cancelled_at"),
        (5, "cancelled but started"),
        (6, "completed before it started"),
        (7, "started before it was created"),
        (10, "cancelled without cancelled_at"),
        (10, "cancelled but started"),
        (10, "started before it was created"),
        (11, "completed_at on a non-completed job"),
        (11, "completed before it started"),
    ]
    assert got == want, ("expected exactly these (job_id, label) pairs sorted by job_id and, inside one job, in the order of the "
                         "table in problem.md. Missing: %s. Unexpected: %s." % ([w for w in want if w not in got], [g for g in got if g not in want]))


def test_clean_jobs_are_not_reported():
    reported = {job_id for job_id, _ in lifecycle_problems(jobs())}
    assert 1 not in reported, "job 1 is clean."
    assert 8 not in reported, "a failed job has no required timestamp: nothing is wrong with job 8."
    assert 9 not in reported, "completed_at equal to started_at is not 'before': use a strict < comparison."


def test_missing_times_do_not_trigger_the_comparison_rules():
    d = jobs().iloc[[1, 2, 3]]
    got = lifecycle_problems(d)
    assert (2, "completed before it started") not in got and (2, "started before it was created") not in got, (
        "when a time is missing (NaT) a comparison is False: do not report it. Job 2 has no completed_at.")
    assert [g for g in got if g[0] == 3] == [(3, "completed_at on a non-completed job")], "job 3 breaks only one rule. Got %s." % got


def test_clean_table_and_input_unchanged():
    d = jobs()
    clean = d[d["job_id"].isin([1, 8, 9])]
    assert lifecycle_problems(clean) == [], "a clean table gives an empty list."
    before = d.copy()
    lifecycle_problems(d)
    pd.testing.assert_frame_equal(d, before)


def test_ids_are_plain_ints():
    got = lifecycle_problems(jobs())
    assert all(type(j) is int and type(label) is str for j, label in got), "return plain int ids and str labels, not numpy values."
