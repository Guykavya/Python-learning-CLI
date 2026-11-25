import pandas as pd

from solution import explain_gap

# The ledger (sql_result): one row per payment.
LEDGER = [
    (1, 400), (1, 600),   # job 1: two payments (1,000)
    (2, 500),             # job 2: one payment
    (3, 300),             # job 3: one payment, one line item: the dashboard agrees (contribution 0)
    (4, 700),             # job 4: has NO line items, so the dashboard's inner join to items loses it
    (5, 200),             # job 5: the dashboard shows a different amount (a typo)
]
# The dashboard: payments joined to line items, one row per (payment, line).
DASH = [
    (1, 400), (1, 600), (1, 400), (1, 600),                  # job 1 has 2 lines: every payment twice
    (2, 500), (2, 500), (2, 500),                            # job 2 has 3 lines: three times
    (3, 300),                                                # job 3 has 1 line
    (5, 250),                                                # job 5: 250 instead of 200
    (6, 150),                                                # job 6: a test payment that is not in the ledger
]


def frames():
    return (pd.DataFrame(DASH, columns=["job_id", "amount"]), pd.DataFrame(LEDGER, columns=["job_id", "amount"]))


def test_gap_and_contributions():
    dash, ledger = frames()
    r = explain_gap(dash, ledger)
    assert r["gap"] == 1500, "dashboard 4,200 minus ledger 2,700 is 1,500. Got %s." % r["gap"]
    assert r["by_job"] == {1: 1000, 2: 1000, 4: -700, 5: 50, 6: 150}, (
        "per job: dashboard sum minus ledger sum; job 3 agrees (leave it out); job 4 is only in the ledger (-700). Got %s." % r["by_job"])
    assert list(r["by_job"]) == [1, 2, 4, 5, 6], "order the jobs by job_id."


def test_contributions_add_up_to_the_gap():
    dash, ledger = frames()
    r = explain_gap(dash, ledger)
    assert sum(r["by_job"].values()) == r["gap"], "the contributions must add up to the gap: a total is a sum over records."
    assert r["unexplained"] == 0, "unexplained = gap - sum of contributions, which is 0 here. Got %s." % r["unexplained"]


def test_reason_labels():
    dash, ledger = frames()
    r = explain_gap(dash, ledger)
    assert r["reasons"] == {
        1: "repeated rows: 4 rows in dashboard, 2 rows in sql result",
        2: "repeated rows: 3 rows in dashboard, 1 rows in sql result",
        4: "only in sql result",
        5: "amount differs",
        6: "only in dashboard",
    }, "reason labels differ. Got %s." % r["reasons"]


def test_types_and_no_change():
    dash, ledger = frames()
    r = explain_gap(dash, ledger)
    assert all(type(k) is int and type(v) is int for k, v in r["by_job"].items()), "job ids and contributions are plain ints."
    assert type(r["gap"]) is int and type(r["unexplained"]) is int, "gap and unexplained are plain ints."
    assert len(dash) == len(DASH) and len(ledger) == len(LEDGER), "do not change the inputs."


def test_equal_tables_have_no_gap():
    _, ledger = frames()
    r = explain_gap(ledger, ledger.copy())
    assert r == {"gap": 0, "by_job": {}, "reasons": {}, "unexplained": 0}, "identical tables: no gap, no jobs. Got %s." % r
