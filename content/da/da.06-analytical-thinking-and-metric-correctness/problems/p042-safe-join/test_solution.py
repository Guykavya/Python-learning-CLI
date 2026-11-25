import pandas as pd
import pytest

from solution import safe_join

JOBS = [(1, 10), (2, 10), (3, 11), (4, 99)]     # job 4's customer 99 is not in the customers table
CUSTOMERS = [(10, "Pune"), (11, "Delhi")]
PAYMENTS = [(1, 400), (1, 600), (2, 500)]       # job 1 has two payments
DUP_CUSTOMERS = [(10, "Pune"), (10, "Pune (old)"), (11, "Delhi")]   # customer 10 twice


def jobs():
    return pd.DataFrame(JOBS, columns=["job_id", "customer_id"])


def customers():
    return pd.DataFrame(CUSTOMERS, columns=["customer_id", "city"])


def payments():
    return pd.DataFrame(PAYMENTS, columns=["job_id", "amount"])


def test_good_join_keeps_rows_and_adds_the_column():
    out = safe_join(jobs(), customers(), on="customer_id", label="jobs + customers")
    assert len(out) == 4, "a left join with a unique right side keeps all 4 jobs (the job with an unknown customer stays, city NaN). Got %d." % len(out)
    assert out["city"].tolist()[:3] == ["Pune", "Pune", "Delhi"] and pd.isna(out["city"].iloc[3]), "the city must be joined by customer_id."


def test_fan_out_is_caught_by_the_row_count():
    with pytest.raises(AssertionError) as e:
        safe_join(jobs(), payments(), on="job_id", validate="1:m", label="jobs + payments")
    assert str(e.value) == "jobs + payments: rows changed 4 -> 5 (fan-out or a lost key?)", (
        "the message must be '<label>: rows changed <before> -> <after> (fan-out or a lost key?)'. Got %r." % str(e.value))


def test_default_label_uses_the_key():
    with pytest.raises(AssertionError) as e:
        safe_join(jobs(), payments(), on="job_id", validate="1:m")
    assert str(e.value).startswith("join on job_id: rows changed 4 -> 5"), "without a label use 'join on <on>'. Got %r." % str(e.value)


def test_wrong_relationship_is_caught_by_pandas():
    with pytest.raises(pd.errors.MergeError):
        safe_join(jobs(), payments(), on="job_id", label="jobs + payments")     # default validate="m:1": payments is not unique on job_id
    with pytest.raises(pd.errors.MergeError):
        safe_join(jobs(), pd.DataFrame(DUP_CUSTOMERS, columns=["customer_id", "city"]), on="customer_id")


def test_inner_join_may_change_the_row_count():
    out = safe_join(jobs(), customers(), on="customer_id", how="inner")
    assert len(out) == 3, "an inner join drops job 4 on purpose: no row-count assertion for how='inner'. Got %d rows." % len(out)


def test_inputs_are_unchanged():
    left, right = jobs(), customers()
    safe_join(left, right, on="customer_id")
    pd.testing.assert_frame_equal(left, jobs())
    pd.testing.assert_frame_equal(right, customers())
