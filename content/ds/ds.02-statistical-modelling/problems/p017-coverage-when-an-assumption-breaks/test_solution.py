import pytest

from solution import slope_ci_coverage


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_clean_world_keeps_its_promise(seed):
    c = slope_ci_coverage("clean", seed=seed)
    assert 0.90 <= c <= 0.99, f"coverage {c:.3f} in the clean world should be near 0.95. Check that the interval is the slope's (row 1 of conf_int) and the truth is 2."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_heteroscedasticity_breaks_the_interval(seed):
    c = slope_ci_coverage("hetero", seed=seed)
    assert c < 0.80, f"coverage {c:.3f}: with spread growing with x the ordinary intervals miss far more than 5%. Is x exponential and e scaled by (0.2 + x)?"


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_autocorrelation_breaks_it_even_more(seed):
    c = slope_ci_coverage("autocorr", seed=seed)
    assert c < 0.70, f"coverage {c:.3f}: with AR(1) errors (0.8) and x = time order about half the intervals miss. Check e[t] = 0.8 * e[t-1] + s[t]."


def test_robust_errors_repair_heteroscedasticity_only():
    plain = slope_ci_coverage("hetero", seed=1)
    robust = slope_ci_coverage("hetero", seed=1, robust=True)
    assert robust > plain + 0.12, f"HC3 coverage {robust:.3f} should be clearly above the ordinary {plain:.3f}. Use fit(cov_type='HC3')."
    assert robust > 0.80, f"HC3 coverage {robust:.3f} should be near 0.9 at n = 50."


def test_same_seed_same_answer():
    assert slope_ci_coverage("clean", reps=60, seed=5) == slope_ci_coverage("clean", reps=60, seed=5), "one default_rng(seed) created outside the loop makes the function repeatable."


def test_unknown_world():
    with pytest.raises(ValueError):
        slope_ci_coverage("sunny")
