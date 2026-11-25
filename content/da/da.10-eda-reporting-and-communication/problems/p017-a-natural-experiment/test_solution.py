import numpy as np
import pandas as pd
import pytest

from solution import price_change_effect


def cell(plan, week, n, churned):
    return pd.DataFrame({"plan": plan, "week": pd.Timestamp(week), "churn_now": np.arange(n) < churned})


def make(c_b, c_a, t_b, t_a):
    """churn counts out of 1,000 rows per cell; before = week of 30 Sep, after = weeks of 7 and 14 Oct."""
    return pd.concat([cell("2-meal", "2024-09-30", 1000, c_b), cell("2-meal", "2024-10-07", 500, c_a // 2), cell("2-meal", "2024-10-14", 500, c_a - c_a // 2),
                      cell("3-meal", "2024-09-30", 1000, t_b), cell("3-meal", "2024-10-07", 500, t_a // 2), cell("3-meal", "2024-10-14", 500, t_a - t_a // 2)],
                     ignore_index=True)


def test_known_effect():
    did = price_change_effect(make(20, 30, 20, 50), "2024-10-07", "3-meal")
    assert did == pytest.approx(2.0), f"treated +3 points, control +1 point: DiD = +2.0, got {did}"


def test_parallel_change_is_zero():
    did = price_change_effect(make(20, 40, 30, 50), "2024-10-07", "3-meal")
    assert did == pytest.approx(0.0), f"both plans rose by 2 points: no extra effect of the price change, got {did}"


def test_change_week_counts_as_after():
    did = price_change_effect(make(20, 30, 20, 50), "2024-10-07", "3-meal")
    later = price_change_effect(make(20, 30, 20, 50), "2024-10-08", "3-meal")
    assert did != pytest.approx(later), "the week starting ON the change date is after (>=); a later date moves that week to before."


def test_treated_can_be_either_plan():
    did = price_change_effect(make(20, 30, 20, 50), "2024-10-07", "2-meal")
    assert did == pytest.approx(-2.0), "with 2-meal as treated, the sign flips."


def test_bad_input():
    df = make(20, 30, 20, 50)
    with pytest.raises(ValueError, match="need exactly two plans"):
        price_change_effect(df, "2024-10-07", "4-meal")
    three = pd.concat([df, cell("4-meal", "2024-09-30", 10, 1)])
    with pytest.raises(ValueError, match="need exactly two plans"):
        price_change_effect(three, "2024-10-07", "3-meal")
