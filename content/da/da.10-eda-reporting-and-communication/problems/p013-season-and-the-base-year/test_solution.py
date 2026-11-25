import numpy as np
import pandas as pd
import pytest

from solution import yoy_change


def monthly(values, start="2023-01"):
    return pd.Series(values, index=pd.period_range(start, periods=len(values), freq="M"), name="churn_pct")


def test_seasonal_series_without_trend_has_zero_change():
    season = [5.0, 4.5, 4.0, 3.8, 3.6, 3.5, 3.6, 3.9, 4.4, 4.8, 5.2, 5.5]
    out = yoy_change(monthly(season * 2))
    assert out.iloc[:12].isna().all(), "the first year has nothing to compare with: NaN."
    assert np.allclose(out.iloc[12:], 0.0), "a seasonal pattern that repeats exactly shows no year-on-year change (month on month it would)."


def test_trend_is_found():
    s = monthly([4.0 + 0.1 * i for i in range(24)])
    out = yoy_change(s)
    assert np.allclose(out.iloc[12:], 1.2), "a rise of 0.1 a month is 1.2 points a year."


def test_matches_by_label_not_position():
    s = monthly([1.0, 2.0, 3.0, 4.0] + [0.0] * 8 + [11.0, 12.0, 13.0, 14.0])
    s = s.drop(pd.Period("2023-03", "M"))
    out = yoy_change(s)
    assert out.loc[pd.Period("2024-03", "M")] != out.loc[pd.Period("2024-03", "M")], "2023-03 is missing: 2024-03 has no comparison (NaN). shift(12) by position compares with the wrong month."
    assert out.loc[pd.Period("2024-04", "M")] == pytest.approx(10.0), "2024-04 (14) against 2023-04 (4): 10."


def test_keeps_index_and_name():
    s = monthly([1.0] * 14)
    out = yoy_change(s)
    assert out.index.equals(s.index), "same index as the input."
    assert out.name == "churn_pct", "keep the series name."
