import pandas as pd

from solution import monthly_counts

# (job_id, created_at, why the row exists)
ROWS = [
    (1, "2025-01-15 10:00:00", "January, a complete month"),
    (2, "2025-01-31 23:59:59", "last second of January: still January"),
    (3, "2025-02-01 00:00:00", "first instant of February: February, not January"),
    (4, "2025-03-31 18:00:00", "March"),
    (5, "2025-04-01 00:00:00", "first instant of April"),
    (6, "2025-04-04 23:00:00", "April, before the cut"),
    (7, "2025-04-05 00:00:00", "exactly at the cut: not in the data"),
    (8, "2025-04-09 10:00:00", "after the cut: not in the data"),
]


def jobs():
    d = pd.DataFrame(ROWS, columns=["job_id", "created_at", "why"]).drop(columns="why")
    d["created_at"] = pd.to_datetime(d["created_at"])
    return d


def test_counts_and_flag_with_cut_inside_april():
    got = monthly_counts(jobs(), "2025-04-05")
    assert list(got.columns) == ["month", "jobs", "is_partial"], "the columns must be month, jobs, is_partial. Got %s." % list(got.columns)
    assert got["month"].tolist() == ["2025-01", "2025-02", "2025-03", "2025-04"], "one row per month with jobs, sorted. Got %s." % got["month"].tolist()
    assert got["jobs"].tolist() == [2, 1, 1, 2], (
        "January has 2 jobs (23:59:59 on the 31st is January), February 1, March 1, April 2 "
        "(the job exactly at the cut and the later one are not in the data). Got %s." % got["jobs"].tolist())
    assert got["is_partial"].tolist() == [False, False, False, True], "only April has not ended at the cut. Got %s." % got["is_partial"].tolist()


def test_cut_exactly_at_a_month_start_makes_the_previous_month_complete():
    got = monthly_counts(jobs(), "2025-04-01")
    assert got["month"].tolist() == ["2025-01", "2025-02", "2025-03"], "at the cut 2025-04-01 there is no April data. Got %s." % got["month"].tolist()
    assert got["is_partial"].tolist() == [False, False, False], (
        "the cut is the first instant of April, so March has ended: March is complete, not partial.")


def test_cut_inside_a_gap_month():
    got = monthly_counts(jobs(), "2025-03-10")
    assert got["month"].tolist() == ["2025-01", "2025-02"], "jobs created after the cut are not in the data. Got %s." % got["month"].tolist()
    assert got["is_partial"].tolist() == [False, False], "the cut is in March, which has no jobs before it: no March row, January and February are complete."


def test_types_index_and_input():
    d = jobs()
    got = monthly_counts(d, pd.Timestamp("2025-04-05"))
    assert list(got.index) == [0, 1, 2, 3], "use a fresh index 0, 1, 2, ... (reset_index)."
    assert all(type(v) is int for v in got["jobs"].tolist()), "jobs must be integers."
    assert all(type(v) is bool for v in got["is_partial"].tolist()), "is_partial must be True/False."
    assert len(d) == 8, "do not drop rows from the caller's table."


def test_empty_result():
    got = monthly_counts(jobs(), "2024-12-31")
    assert len(got) == 0 and list(got.columns) == ["month", "jobs", "is_partial"], "no job before the cut: an empty table with the same columns."
