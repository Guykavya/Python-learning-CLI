import pytest

from solution import omitted_bias


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_long_model_recovers_the_true_effect(seed):
    out = omitted_bias(4000, seed)
    assert out["long_slope"] == pytest.approx(2.0, abs=0.25), f"long slope {out['long_slope']:.2f}: with ability in the model the effect of one coaching hour is about 2. Check hours = 0.8 * ability + noise and score = 50 + 2 * hours + 5 * ability + noise."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_short_model_is_biased_upwards(seed):
    out = omitted_bias(4000, seed)
    assert out["short_slope"] > 3.9, f"short slope {out['short_slope']:.2f}: leaving out ability should inflate the hours effect to about 4.4."
    assert out["short_slope"] == pytest.approx(4.44, abs=0.4), "expected about 2 + 5 * 0.8 / 1.64 = 4.44."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_bias_formula_is_exact_in_a_sample(seed):
    out = omitted_bias(2000, seed)
    assert out["predicted_short"] == pytest.approx(out["short_slope"], rel=1e-8), "short = long_hours + b_ability * delta holds exactly, where delta = cov(ability, hours) / var(hours) (same divisor in both)."


def test_bias_does_not_shrink_with_more_data():
    small = omitted_bias(500, 3)
    large = omitted_bias(20000, 3)
    assert abs(large["short_slope"] - 2.0) > 2.0, "even with 20,000 rows the short model stays far from 2: more data does not remove omitted-variable bias."
    assert abs(small["short_slope"] - 2.0) > 1.5, "the bias is already there with 500 rows."
