import pandas as pd
import pytest

from solution import items_per_customer, items_per_job


def jobs():
    return pd.DataFrame({
        "job_id": [1, 2, 3, 4, 5],
        "customer_id": [1, 1, 1, 2, 3],        # customer 1 has three jobs, customers 2 and 3 one each
    })


def items():
    return pd.DataFrame({
        "job_id": [1, 1, 1, 2, 3, 3, 4, 99],   # job 1: 3 lines, job 2: 1, job 3: 2, job 4: 1, job 5: none; job 99 does not exist
        "line_no": [1, 2, 3, 1, 1, 2, 1, 1],
    })


def test_items_per_job():
    got = items_per_job(jobs(), items())
    assert got == pytest.approx(7 / 5), ("7 line items belong to the 5 jobs (the line of the unknown job 99 is nobody's, and job 5 "
                                         "with no line still counts as a job): 7 / 5 = 1.4. Got %s." % got)


def test_items_per_customer():
    got = items_per_customer(jobs(), items())
    assert got == pytest.approx(7 / 3), "7 line items over the 3 customers who have a job: 7 / 3 = 2.33. Got %s." % got


def test_the_unit_changes_the_answer():
    assert items_per_job(jobs(), items()) != pytest.approx(items_per_customer(jobs(), items())), (
        "per job and per customer are different questions with different answers.")


def test_job_without_items_still_counts_in_the_denominator():
    one = pd.DataFrame({"job_id": [1, 2], "customer_id": [1, 2]})
    its = pd.DataFrame({"job_id": [1, 1], "line_no": [1, 2]})
    assert items_per_job(one, its) == pytest.approx(1.0), "2 lines over 2 jobs = 1.0; job 2 has no lines but is still a job (do not merge inner)."


def test_no_jobs_gives_none():
    empty = pd.DataFrame({"job_id": [], "customer_id": []})
    assert items_per_job(empty, items()) is None and items_per_customer(empty, items()) is None, "with no jobs there is no average: None."


def test_plain_floats_and_inputs_unchanged():
    j, i = jobs(), items()
    j0, i0 = j.copy(), i.copy()
    assert type(items_per_job(j, i)) is float and type(items_per_customer(j, i)) is float, "return plain floats."
    pd.testing.assert_frame_equal(j, j0)
    pd.testing.assert_frame_equal(i, i0)
