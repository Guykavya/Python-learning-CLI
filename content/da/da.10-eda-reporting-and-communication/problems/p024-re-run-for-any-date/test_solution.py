import numpy as np
import pandas as pd
import pytest

from solution import quick_summary


def base():
    cus = pd.DataFrame({"customer_id": [1, 2, 3], "last_week": pd.to_datetime(["2024-01-15", pd.NaT, pd.NaT])})
    weeks = {1: ["2024-01-01", "2024-01-08", "2024-01-15"], 2: ["2024-01-01", "2024-01-08", "2024-01-15", "2024-01-22", "2024-01-29", "2024-02-05", "2024-02-12"],
             3: ["2024-01-01", "2024-01-08", "2024-01-15", "2024-01-22", "2024-01-29", "2024-02-05", "2024-02-12"]}
    rows = [{"customer_id": c, "week": pd.Timestamp(w), "late": (c == 3 and w == "2024-01-08"), "price": 100} for c, ws in weeks.items() for w in ws]
    return cus, pd.DataFrame(rows)


def with_future(cus, pan):
    cus = cus.copy()
    cus.loc[cus["customer_id"] == 2, "last_week"] = pd.Timestamp("2024-02-19")                    # leaves after as_of
    cus = pd.concat([cus, pd.DataFrame({"customer_id": [4], "last_week": [pd.NaT]})], ignore_index=True)
    future = [{"customer_id": c, "week": pd.Timestamp(w), "late": True, "price": 100}
              for c, w in [(2, "2024-02-19"), (3, "2024-02-19"), (3, "2024-02-26"), (3, "2024-03-04"), (4, "2024-02-26"), (4, "2024-03-04")]]
    return cus, pd.concat([pan, pd.DataFrame(future)], ignore_index=True)


def test_last_complete_month():
    s = quick_summary(*base(), "2024-02-14")
    assert s["last_month"] == "2024-01", f"as of 14 February the last complete month is January, got {s['last_month']}"
    assert s["months"] == 1, "only January is complete."
    assert s["as_of"] == "2024-02-14"


def test_january_values():
    s = quick_summary(*base(), "2024-02-14")
    assert s["opening_last"] == 3 and s["churn_last"] == pytest.approx(100 / 3), f"January: 3 opening actives, 1 churned; got {s}"
    assert s["on_time_last"] == pytest.approx((1 - 1 / 13) * 100), "1 late box of 13 January rows."


def test_future_data_does_not_leak():
    before = quick_summary(*base(), "2024-02-14")
    after = quick_summary(*with_future(*base()), "2024-02-14")
    assert after == before, f"future data leaked into the report: {before} became {after}"


def test_a_later_as_of_moves_forward():
    s = quick_summary(*with_future(*base()), "2024-03-10")
    assert s["last_month"] == "2024-02" and s["months"] == 2, "as of 10 March, February is complete."
    assert s["churn_last"] == pytest.approx(50.0), "February: customers 2 and 3 open it, customer 2 leaves on 19 February (known by 10 March)."


def test_plain_types():
    s = quick_summary(*base(), "2024-02-14")
    assert type(s["opening_last"]) is int and type(s["churn_last"]) is float and type(s["months"]) is int, "return plain Python ints and floats."
