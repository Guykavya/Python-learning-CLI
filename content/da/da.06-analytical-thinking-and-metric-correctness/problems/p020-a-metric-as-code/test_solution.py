import dataclasses

import pandas as pd
import pytest

from solution import METRICS, Metric, compute

FEB = (pd.Timestamp("2025-02-01"), pd.Timestamp("2025-03-01"))


def jobs():
    rows = [
        # id, customer, created_at,           status,      completed_at           why this row exists
        (1, 1,  "2025-02-01 00:00:00", "completed", "2025-02-03 12:00:00"),     # created exactly at the start
        (2, 2,  "2025-02-10 09:00:00", "completed", "2025-03-01 00:00:00"),  # completed exactly at the end: March
        (3, 3,  "2025-02-15 09:00:00", "completed", "2025-02-20 12:00:00"),
        (4, 1,  "2025-02-20 09:00:00", "cancelled", None),
        (5, 2,  "2025-02-25 09:00:00", "failed",    None),
        (6, 3,  "2025-02-28 09:00:00", "pending",   None),             # no outcome yet
        (7, 99, "2025-02-12 09:00:00", "completed", "2025-02-14 12:00:00"),     # customer 99 is a test account
        (8, 4,  "2025-01-31 23:59:00", "completed", "2025-02-02 12:00:00"),     # created in January, completed in February
        (9, 4,  "2025-03-01 00:00:00", "completed", "2025-03-02 12:00:00"),     # created exactly at the end: March
    ]
    df = pd.DataFrame(rows, columns=["job_id", "customer_id", "created_at", "status", "completed_at"])
    df["created_at"] = pd.to_datetime(df["created_at"])
    df["completed_at"] = pd.to_datetime(df["completed_at"])
    return df


def test_metric_has_the_five_fields_and_is_frozen():
    m = Metric(name="x", numerator=("completed",), denominator=None, date_basis="created_at", exclusions=(99,))
    assert (m.name, m.numerator, m.denominator, m.date_basis, m.exclusions) == ("x", ("completed",), None, "created_at", (99,)), (
        "Metric needs the fields name, numerator, denominator, date_basis, exclusions, in that order.")
    with pytest.raises(dataclasses.FrozenInstanceError):
        m.name = "y"


def test_exclusions_default_to_nothing():
    m = Metric("x", ("completed",), None, "created_at")
    assert m.exclusions == (), "exclusions must default to an empty tuple."


def test_jobs_completed_in_february_uses_completed_at_and_skips_test_accounts():
    got = compute(METRICS["jobs_completed"], jobs(), *FEB)
    assert got == 3, ("completed in February by completed_at: jobs 1 (Feb 3), 3 (Feb 20) and 8 (Feb 2). Job 2 completed exactly at "
                      "the end (March), job 7 belongs to the test account 99. Got %s." % got)


def test_completion_rate_by_created_at():
    got = compute(METRICS["completion_rate"], jobs(), *FEB)
    assert got == pytest.approx(3 / 5), ("created in February (test account out): jobs 1-6; decided = completed, cancelled, failed "
                                         "= jobs 1, 2, 3, 4, 5 (pending job 6 is out); completed = 1, 2, 3. 3 / 5 = 0.6. Got %s." % got)


def test_march_period_is_half_open_at_the_start():
    got = compute(METRICS["completion_rate"], jobs(), pd.Timestamp("2025-03-01"), pd.Timestamp("2025-04-01"))
    assert got == pytest.approx(1.0), "job 9 is created exactly at the start of March and belongs to it: 1 completed of 1 decided."


def test_a_count_returns_an_int():
    got = compute(METRICS["jobs_completed"], jobs(), *FEB)
    assert type(got) is int, "a metric without a denominator returns a plain int."


def test_rate_with_empty_denominator_is_none():
    got = compute(METRICS["completion_rate"], jobs(), pd.Timestamp("2026-01-01"), pd.Timestamp("2026-02-01"))
    assert got is None, "no decided jobs, no rate: None."


def test_exclusions_really_matter():
    open_metric = dataclasses.replace(METRICS["jobs_completed"], exclusions=())
    assert compute(open_metric, jobs(), *FEB) == 4, "without the exclusion the test account's job 7 is counted too: 4."


def test_registry_has_the_two_named_metrics():
    assert set(METRICS) == {"jobs_completed", "completion_rate"}, "register exactly two metrics under their names."
    assert METRICS["jobs_completed"].name == "jobs_completed" and METRICS["completion_rate"].name == "completion_rate"
    assert METRICS["completion_rate"].denominator == ("completed", "cancelled", "failed"), "the denominator lists the decided statuses."


def test_accepts_date_strings_and_leaves_jobs_alone():
    j = jobs()
    before = j.copy()
    assert compute(METRICS["jobs_completed"], j, "2025-02-01", "2025-03-01") == 3
    pd.testing.assert_frame_equal(j, before)
