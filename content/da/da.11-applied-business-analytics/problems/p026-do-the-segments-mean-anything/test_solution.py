import numpy as np
import pandas as pd
import pytest

from solution import future_value_by_segment

RFM = pd.DataFrame({"segment": ["Champions", "Champions", "Hibernating", "Hibernating", "Hibernating", "Loyal"]}, index=[1, 2, 3, 4, 5, 6])
RFM.index.name = "customer_id"
AFTER = pd.DataFrame({"customer_id": [1, 1, 2, 3, 99], "amount": [100.0, 50.0, 70.0, 30.0, 5000.0]})


def test_hand_values():
    t = future_value_by_segment(RFM, AFTER)
    assert list(t.columns) == ["customers", "bought_again_pct", "future_spend_per_customer"], f"columns, got {list(t.columns)}"
    assert t.loc["Champions"].tolist() == pytest.approx([2, 100.0, 110.0]), "Champions: customers 1 and 2 both bought again; (150 + 70) / 2 = 110 per customer."
    assert t.loc["Hibernating"].tolist() == pytest.approx([3, 100 / 3, 10.0]), "Hibernating: only customer 3 bought (30); 30 / 3 customers = 10, and 33.3% bought again."


def test_zero_spend_segments_are_kept_and_unknown_customers_ignored():
    t = future_value_by_segment(RFM, AFTER)
    assert t.loc["Loyal"].tolist() == pytest.approx([1, 0.0, 0.0]), "a segment whose customers bought nothing stays with spend 0 (do not drop it)."
    assert t["customers"].sum() == 6, "customer 99 is not in rfm: ignored."


def test_sorted_best_first():
    t = future_value_by_segment(RFM, AFTER)
    assert list(t.index) == ["Champions", "Hibernating", "Loyal"], f"largest future spend per customer first, got {list(t.index)}"
    assert t["customers"].dtype.kind == "i"
