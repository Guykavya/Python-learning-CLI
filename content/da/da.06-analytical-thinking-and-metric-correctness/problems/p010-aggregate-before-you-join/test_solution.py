import pandas as pd

from solution import paid_per_customer


def jobs():
    return pd.DataFrame({
        "job_id": [5001, 5002, 5003, 5004, 5005],
        "customer_id": [1, 1, 2, 3, 2],
        "quote_total": [1000, 400, 700, 300, 200],
    })


def payments():
    return pd.DataFrame({
        "payment_id": [1, 2, 3, 4, 5],
        "job_id": [5001, 5001, 5002, 5003, 9999],     # job 5001: deposit + balance; 9999 is not a job
        "amount": [300, 700, 400, 700, 50],
    })


def test_quoted_is_not_multiplied_by_the_number_of_payments():
    got = paid_per_customer(jobs(), payments()).to_dict("index")
    assert got[1]["quoted"] == 1400, ("customer 1 quoted 1000 + 400 = 1400. Got %s: job 5001 has two payments, so a plain "
                                      "join repeats its quote twice. Sum the payments per job BEFORE the join." % got[1]["quoted"])


def test_full_result():
    got = paid_per_customer(jobs(), payments()).to_dict("index")
    want = {1: {"quoted": 1400, "paid": 1400}, 2: {"quoted": 900, "paid": 700}, 3: {"quoted": 300, "paid": 0}}
    assert got == want, "expected %s, got %s. A customer whose job has no payment is kept, with paid = 0." % (want, got)


def test_total_paid_equals_payments_of_existing_jobs():
    out = paid_per_customer(jobs(), payments())
    assert int(out["paid"].sum()) == 2100, ("the payments of jobs that exist add up to 300+700+400+700 = 2100; the payment "
                                            "of the unknown job 9999 (50) is not paid by any customer. Got %s." % int(out["paid"].sum()))


def test_one_row_per_customer_and_integer_columns():
    out = paid_per_customer(jobs(), payments())
    assert list(out.index) == [1, 2, 3], "one row per customer, sorted by customer_id. Got index %s." % list(out.index)
    assert out.index.name == "customer_id", "the index must be named customer_id (use groupby)."
    assert str(out["paid"].dtype).startswith("int") and str(out["quoted"].dtype).startswith("int"), (
        "both columns must be integers; after a left join missing sums are float, convert back with fillna(0) and astype(int).")


def test_inputs_are_not_changed():
    j, p = jobs(), payments()
    j0, p0 = j.copy(), p.copy()
    paid_per_customer(j, p)
    pd.testing.assert_frame_equal(j, j0)
    pd.testing.assert_frame_equal(p, p0)
