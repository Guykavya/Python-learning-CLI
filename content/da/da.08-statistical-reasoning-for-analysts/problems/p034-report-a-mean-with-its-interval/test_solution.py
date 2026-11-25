import math

import numpy as np
import pytest
from scipy import stats
from solution import report_mean


def expected(x, label, unit, level):
    x = np.asarray(x, float)
    x = x[~np.isnan(x)]
    se = x.std(ddof=1) / math.sqrt(len(x))
    h = stats.t.ppf((1 + level) / 2, len(x) - 1) * se
    d = max(0, 1 - math.floor(math.log10(se)))
    f = lambda v: f"{round(v, d):,.{d}f}"
    return f"{label}: {f(x.mean())}{unit} ({int(round(level * 100))}% CI {f(x.mean() - h)} to {f(x.mean() + h)}; n = {len(x):,})"


def test_hand_example():
    assert report_mean([10, 12, 14, 16, 18], "Mean weight", " kg") == "Mean weight: 14.0 kg (95% CI 10.1 to 17.9; n = 5)"


def test_nan_is_dropped_and_not_counted():
    assert report_mean([10, 12, float("nan"), 14, 16, 18], "Mean weight", " kg") == "Mean weight: 14.0 kg (95% CI 10.1 to 17.9; n = 5)", \
        "Drop NaN first; n counts only the real values."


def test_exact_format_on_random_data():
    x = np.random.default_rng(5).normal(2500, 500, 500)
    assert report_mean(x, "Mean monthly spend", " rupees") == expected(x, "Mean monthly spend", " rupees", 0.95), \
        "Format: 'label: mean unit (95% CI lo to hi; n = 500)' with the numbers rounded by sig_round(value, SE)."


def test_level_90_and_thousands_separator_in_n():
    x = np.random.default_rng(6).normal(100, 20, 1500)
    r = report_mean(x, "Mean", "", level=0.9)
    assert "(90% CI " in r and "n = 1,500" in r, "level=0.9 prints '90% CI'; n = 1,500 has a thousands separator."
    assert r == expected(x, "Mean", "", 0.9)


def test_too_few_values():
    with pytest.raises(ValueError):
        report_mean([5.0, float("nan")], "x")
