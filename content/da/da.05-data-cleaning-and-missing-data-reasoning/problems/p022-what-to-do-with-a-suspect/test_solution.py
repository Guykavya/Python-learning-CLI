import numpy as np
import pandas as pd
import pytest

from solution import outlier_strategies


def test_worked_example():
    s = pd.Series([1, 2, 3, 4, 100])
    out = outlier_strategies(s, s > 50)
    assert set(out) == {"keep", "remove", "cap", "flag_only"}, "the result needs exactly the keys keep, remove, cap, flag_only."
    assert out["keep"] == pytest.approx({"mean": 22.0, "median": 3.0}), "keep: statistics of all five values (mean 22, median 3)."
    assert out["remove"] == pytest.approx({"mean": 2.5, "median": 2.5}), "remove: statistics of [1, 2, 3, 4]."
    assert out["cap"] == pytest.approx({"mean": 3.4, "median": 3.0}), (
        "cap: Q1=2, Q3=4, upper fence 7, so 100 becomes 7: values [1, 2, 3, 4, 7].")
    assert out["flag_only"] == pytest.approx({"mean": 22.0, "median": 3.0, "n_flagged": 1}), (
        "flag_only changes nothing, but reports n_flagged.")


def test_choice_moves_mean_not_median():
    rng = np.random.default_rng(3)
    s = pd.Series(np.concatenate([rng.normal(50, 5, 200), [900.0, 1200.0, 800.0]]))
    out = outlier_strategies(s, s > 500)
    assert out["keep"]["mean"] > out["remove"]["mean"] + 10, "keeping three huge values must lift the mean well above the 'remove' mean."
    assert out["keep"]["mean"] > out["cap"]["mean"] > out["remove"]["mean"] - 1, "the capped mean lies between 'keep' and about 'remove'."
    assert abs(out["keep"]["median"] - out["remove"]["median"]) < 1.0, "the median hardly moves with three suspects among 203 values."


def test_cap_changes_only_flagged_values():
    s = pd.Series([1.0, 2.0, 3.0, 4.0, 40.0, 100.0])
    flags = pd.Series([False, False, False, False, False, True])   # 40 is above the fence but NOT flagged
    out = outlier_strategies(s, flags)
    q1, q3 = s.quantile([0.25, 0.75])
    hi = q3 + 1.5 * (q3 - q1)
    want = (1 + 2 + 3 + 4 + 40 + hi) / 6
    assert out["cap"]["mean"] == pytest.approx(want), (
        "only the flagged value (100) is capped at the fence %.2f; 40 is above the fence but not flagged, so it stays." % hi)


def test_flagged_value_inside_the_fences_is_unchanged():
    s = pd.Series([10.0, 11.0, 12.0, 13.0, 14.0])
    flags = pd.Series([False, False, False, False, True])
    out = outlier_strategies(s, flags)
    assert out["cap"]["mean"] == pytest.approx(12.0), "14 is inside the fences, so capping must not change it."
    assert out["remove"]["mean"] == pytest.approx(11.5)


def test_missing_values_are_skipped():
    s = pd.Series([1.0, np.nan, 3.0, 5.0, 100.0, np.nan])
    flags = pd.Series([False, False, False, False, True, False])
    out = outlier_strategies(s, flags)
    assert out["keep"]["mean"] == pytest.approx(27.25), "the statistics skip missing values: (1+3+5+100)/4."
    assert out["remove"]["mean"] == pytest.approx(3.0), "removing the suspect leaves 1, 3, 5 (the missing values are skipped)."
    assert out["flag_only"]["n_flagged"] == 1


def test_types_and_inputs_not_changed():
    s = pd.Series([1, 2, 3, 4, 100])
    flags = s > 50
    s0, f0 = s.copy(), flags.copy()
    out = outlier_strategies(s, flags)
    pd.testing.assert_series_equal(s, s0)
    pd.testing.assert_series_equal(flags, f0)
    assert type(out["keep"]["mean"]) is float and type(out["flag_only"]["n_flagged"]) is int, (
        "use float(...) for mean and median and int(...) for n_flagged.")
