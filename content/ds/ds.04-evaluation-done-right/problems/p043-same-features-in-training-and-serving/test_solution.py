import numpy as np
import pandas as pd
import pytest

from conftest import make_churn
from solution import build_features

COLS = ["tenure_months", "charge_per_call", "contract_month", "contract_year", "contract_two_year", "autopay"]


@pytest.fixture(scope="module")
def raw():
    return make_churn(n=50, seed=3).drop(columns=["churned", "region"])


def test_columns_and_index(raw):
    f = build_features(raw)
    assert list(f.columns) == COLS, f"exactly these columns in this order: {COLS}."
    assert list(f.index) == list(raw.index), "keep the index of raw."


def test_batch_equals_one_row_at_a_time(raw):
    batch = build_features(raw)
    for i in range(len(raw)):
        single = build_features(raw.iloc[[i]])
        pd.testing.assert_frame_equal(single, batch.iloc[[i]], check_dtype=False, obj=f"row {i}: one-at-a-time features differ from batch features (training-serving skew)")


def test_one_row_has_all_contract_columns():
    row = pd.DataFrame({"tenure_months": [100], "monthly_charge": [60.0], "support_calls": [2], "contract": ["year"], "autopay": [True]})
    f = build_features(row)
    assert f.iloc[0].tolist() == pytest.approx([72, 20.0, 0, 1, 0, 1]), "tenure clipped to 72; 60 / (1 + 2) = 20; one-hot year; autopay 1."


def test_unknown_contract_is_all_zero_and_raw_unchanged(raw):
    row = raw.iloc[[0]].copy()
    row["contract"] = "weekly"
    before = row.copy()
    f = build_features(row)
    assert f[["contract_month", "contract_year", "contract_two_year"]].iloc[0].tolist() == [0, 0, 0], "an unseen contract value gives zeros, not a new column or an error."
    pd.testing.assert_frame_equal(row, before)
