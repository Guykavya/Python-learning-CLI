import pandas as pd
import pytest
from solution import adjusted_diff

DF = pd.DataFrame({"g": ["mild"] * 4 + ["severe"] * 4, "t": [1, 0, 0, 0, 1, 1, 1, 0], "y": [80, 70, 70, 70, 50, 50, 50, 40]})


def test_simpsons_paradox():
    naive = DF.loc[DF.t == 1, "y"].mean() - DF.loc[DF.t == 0, "y"].mean()
    adj, skipped = adjusted_diff(DF, "t", "y", "g")
    assert naive == -5.0, "Sanity check: the naive difference is negative."
    assert adj == pytest.approx(10.0), "Inside each group the treatment helps by 10; the adjusted difference is +10, the naive one -5."
    assert skipped == []


def test_unequal_weights():
    df = pd.DataFrame({"g": ["a"] * 6 + ["b"] * 2, "t": [1, 1, 0, 0, 0, 0, 1, 0], "y": [10, 12, 6, 6, 6, 6, 30, 20]})
    adj, _ = adjusted_diff(df, "t", "y", "g")
    assert adj == pytest.approx((6 * 5.0 + 2 * 10.0) / 8), "Weight each stratum difference by its number of rows (6 and 2)."


def test_strata_without_both_groups_are_skipped_and_reported():
    extra = pd.DataFrame({"g": ["z", "z", "y"], "t": [0, 0, 1], "y": [1000, 2000, -500]})
    adj, skipped = adjusted_diff(pd.concat([DF, extra], ignore_index=True), "t", "y", "g")
    assert skipped == ["y", "z"], "Strata 'y' (no control) and 'z' (no treated) must be skipped, sorted, and reported."
    assert adj == pytest.approx(10.0), "Skipped strata must not enter the weights."


def test_boolean_treatment_column():
    df = DF.assign(t=DF["t"].astype(bool))
    assert adjusted_diff(df, "t", "y", "g")[0] == pytest.approx(10.0)


def test_no_usable_stratum():
    df = pd.DataFrame({"g": ["a", "b"], "t": [1, 0], "y": [1, 2]})
    with pytest.raises(ValueError):
        adjusted_diff(df, "t", "y", "g")
