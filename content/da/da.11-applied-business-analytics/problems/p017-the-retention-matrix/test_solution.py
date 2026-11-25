import numpy as np
import pandas as pd
import pytest

from solution import retention_matrix

CUS = pd.DataFrame({"customer_id": ["A", "B", "C", "D"],
                    "first_order": pd.to_datetime(["2024-01-05", "2024-01-20", "2024-02-02", "2024-03-01"])})
ORD = pd.DataFrame({"customer_id": ["A", "A", "A", "B", "C", "C", "D", "D"],
                    "order_date": pd.to_datetime(["2024-01-05", "2024-02-10", "2024-03-03", "2024-01-20", "2024-02-02", "2024-02-20", "2024-03-01", "2024-04-20"])})
ASOF = "2024-03-15"


def m():
    return retention_matrix(ORD, CUS, ASOF)


def test_shape_and_labels():
    t = m()
    assert list(t.index.astype(str)) == ["2024-01", "2024-02", "2024-03"], f"one row per cohort month, sorted; got {list(t.index.astype(str))}"
    assert list(t.columns) == [0, 1, 2], f"columns 0..2 (the oldest cohort has been observed for 3 months), got {list(t.columns)}"


def test_values():
    t = m()
    assert t.loc[pd.Period("2024-01", "M")].tolist() == [1.0, 0.5, 0.5], "January cohort (A, B): month 0 both, February only A, March only A."
    c = t.loc[pd.Period("2024-02", "M")]
    assert c[0] == 1.0 and c[1] == 0.0, "February cohort: C ordered twice in month 0 (counts once); nobody in March: 0.0 (observed, so a real zero)."
    assert np.isnan(c[2]), "April has not happened by 15 March: NaN."


def test_unobserved_cells_are_nan_not_zero():
    t = m()
    d = t.loc[pd.Period("2024-03", "M")]
    assert d[0] == 1.0 and np.isnan(d[1]) and np.isnan(d[2]), "the March cohort has only month 0 so far; D's order on 20 April is after asof and ignored; the rest is NaN, not 0."


def test_counts_distinct_customers():
    orders = pd.concat([ORD, pd.DataFrame({"customer_id": ["B", "B"], "order_date": pd.to_datetime(["2024-02-01", "2024-02-28"])})])
    assert retention_matrix(orders, CUS, ASOF).loc[pd.Period("2024-01", "M"), 1] == 1.0, "A and B both ordered in February (B twice): 2 distinct customers of 2."
