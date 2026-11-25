import pandas as pd
import pytest
from solution import weighted_mean

DF = pd.DataFrame({"city": ["Metro", "Metro", "Small", "Small", "Small"], "spend": [100, 120, 50, 70, 60]})


def test_hand_example():
    assert weighted_mean(DF, "spend", "city", {"Metro": 0.3, "Small": 0.7}) == pytest.approx(75.0), \
        "Weight the stratum means by the POPULATION shares: 0.3 * 110 + 0.7 * 60 = 75 (the plain mean is 80)."


def test_equal_shares():
    assert weighted_mean(DF, "spend", "city", {"Metro": 0.5, "Small": 0.5}) == pytest.approx(85.0)


def test_three_strata():
    df = pd.DataFrame({"g": ["a", "b", "c", "c"], "v": [10, 20, 30, 50]})
    assert weighted_mean(df, "v", "g", {"a": 0.2, "b": 0.3, "c": 0.5}) == pytest.approx(0.2 * 10 + 0.3 * 20 + 0.5 * 40)


def test_stratum_without_rows():
    with pytest.raises(ValueError, match="Rural"):
        weighted_mean(DF, "spend", "city", {"Metro": 0.3, "Small": 0.5, "Rural": 0.2})


def test_sample_stratum_not_in_shares():
    with pytest.raises(ValueError, match="Small"):
        weighted_mean(DF, "spend", "city", {"Metro": 1.0})


def test_shares_must_add_to_one():
    with pytest.raises(ValueError):
        weighted_mean(DF, "spend", "city", {"Metro": 0.3, "Small": 0.6})
