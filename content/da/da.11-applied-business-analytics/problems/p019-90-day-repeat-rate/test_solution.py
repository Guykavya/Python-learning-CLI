import numpy as np
import pandas as pd
import pytest

from solution import repeat_rate_90d

ASOF = "2024-12-31"
FIRST = {"a": "2024-03-01", "b": "2024-04-01", "c": "2024-10-02", "d": "2024-10-03", "e": "2024-05-01", "f": "2024-06-01"}
CUS = pd.DataFrame({"customer_id": list(FIRST), "first_order": pd.to_datetime(list(FIRST.values()))})
ORD = pd.DataFrame([
    ("a", "2024-03-01"), ("a", "2024-05-15"),            # second order after 75 days: repeater
    ("b", "2024-04-01"), ("b", "2024-08-01"),            # second order after 122 days: not a repeater
    ("c", "2024-10-02"), ("c", "2024-12-31"),            # eligible at exactly 90 days; second order exactly 90 days later: repeater
    ("d", "2024-10-03"), ("d", "2024-10-10"),            # acquired 89 days before asof: not eligible at all
    ("e", "2024-05-01"),                                 # never reordered
    ("f", "2024-06-01"), ("f", "2024-06-01"),            # two orders on the first day: second order after 0 days, repeater
], columns=["customer_id", "order_date"]).assign(order_date=lambda d: pd.to_datetime(d["order_date"]))


def test_counts():
    r = repeat_rate_90d(ORD, CUS, ASOF)
    assert r["eligible"] == 5, f"d is not eligible (89 days); a, b, c, e, f are: 5, got {r['eligible']}"
    assert r["repeaters"] == 3, f"a (75 days), c (exactly 90 days) and f (same day) repeat; got {r['repeaters']}"
    assert r["rate_pct"] == pytest.approx(60.0)


def test_boundary_customers():
    only_c = repeat_rate_90d(ORD[ORD["customer_id"] == "c"], CUS[CUS["customer_id"] == "c"], ASOF)
    assert only_c["eligible"] == 1 and only_c["repeaters"] == 1, "exactly 90 days before asof is eligible, and exactly 90 days to the second order counts."
    only_d = repeat_rate_90d(ORD[ORD["customer_id"] == "d"], CUS[CUS["customer_id"] == "d"], ASOF)
    assert only_d["eligible"] == 0 and np.isnan(only_d["rate_pct"]), "89 days of follow-up is not enough: nobody eligible, NaN rate."


def test_naive_denominator_is_wrong():
    r = repeat_rate_90d(ORD, CUS, ASOF)
    assert r["rate_pct"] != pytest.approx(3 / 6 * 100), "do not divide by all six customers."


def test_plain_types():
    r = repeat_rate_90d(ORD, CUS, ASOF)
    assert type(r["eligible"]) is int and type(r["repeaters"]) is int and type(r["rate_pct"]) is float
