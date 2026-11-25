import numpy as np
import pandas as pd
import pytest

from conftest import make_population
from solution import simulate_missing

SEEDS = [1, 2, 3]


@pytest.mark.parametrize("mechanism", ["MCAR", "MAR", "MNAR"])
@pytest.mark.parametrize("seed", SEEDS)
def test_rate_is_close_to_the_target(mechanism, seed):
    pop = make_population(6000, seed)
    out = simulate_missing(pop, mechanism, 0.25, np.random.default_rng(seed + 100))
    share = out["income"].isna().mean()
    assert abs(share - 0.25) < 0.02, (
        "%s: the share of missing incomes must be within 2 points of the target 0.25, got %.3f. Did you divide the weights by their mean?"
        % (mechanism, share))


@pytest.mark.parametrize("seed", SEEDS)
def test_returns_a_copy_and_only_income_changes(seed):
    pop = make_population(3000, seed)
    before = pop.copy()
    out = simulate_missing(pop, "MAR", 0.3, np.random.default_rng(5))
    pd.testing.assert_frame_equal(pop, before, obj="pop (the input must not change)")
    assert out is not pop, "return a copy."
    pd.testing.assert_frame_equal(out[["edu_years", "age"]], pop[["edu_years", "age"]], obj="edu_years and age")
    kept = out["income"].notna()
    assert (out.loc[kept, "income"] == pop.loc[kept, "income"]).all(), "incomes that survive must keep their value."
    assert out.index.equals(pop.index), "keep the index."


def test_same_seed_same_result():
    pop = make_population(2000, 4)
    a = simulate_missing(pop, "MNAR", 0.2, np.random.default_rng(11))
    b = simulate_missing(pop, "MNAR", 0.2, np.random.default_rng(11))
    pd.testing.assert_frame_equal(a, b, obj="two runs with the same seed")


@pytest.mark.parametrize("seed", SEEDS)
def test_mcar_hides_young_and_old_alike(seed):
    pop = make_population(6000, seed)
    out = simulate_missing(pop, "MCAR", 0.25, np.random.default_rng(seed + 100))
    m = out["income"].isna()
    young, old = m[pop["age"] < 40].mean(), m[pop["age"] >= 40].mean()
    assert 0.7 < young / old < 1.4, "MCAR is a coin flip: the missing rate must not depend on age (under 40: %.3f, 40+: %.3f)." % (young, old)


@pytest.mark.parametrize("seed", SEEDS)
def test_mar_hides_the_young_more_often(seed):
    pop = make_population(6000, seed)
    out = simulate_missing(pop, "MAR", 0.25, np.random.default_rng(seed + 100))
    m = out["income"].isna()
    young, old = m[pop["age"] < 40].mean(), m[pop["age"] >= 40].mean()
    assert young > 1.5 * old, (
        "MAR by age: people under 40 hide about twice as often (weights 2 and 1). Got %.3f under 40 and %.3f for 40+." % (young, old))


@pytest.mark.parametrize("seed", SEEDS)
def test_mnar_complete_case_mean_is_too_low(seed):
    pop = make_population(6000, seed)
    out = simulate_missing(pop, "MNAR", 0.25, np.random.default_rng(seed + 100))
    truth, observed = pop["income"].mean(), out["income"].mean()
    assert observed < 0.95 * truth, (
        "MNAR: high earners hide five times as often, so the mean of the incomes that remain must be at least 5%% below "
        "the truth. Truth %.0f, observed %.0f. Is the weight 5 for incomes ABOVE the median?" % (truth, observed))


@pytest.mark.parametrize("seed", SEEDS)
def test_mcar_complete_case_mean_is_close_to_the_truth(seed):
    pop = make_population(6000, seed)
    out = simulate_missing(pop, "MCAR", 0.25, np.random.default_rng(seed + 100))
    assert abs(out["income"].mean() / pop["income"].mean() - 1) < 0.03, "MCAR must not bias the mean of the incomes that remain."


def test_unknown_mechanism_raises():
    pop = make_population(100, 1)
    with pytest.raises(ValueError):
        simulate_missing(pop, "MAYBE", 0.2, np.random.default_rng(0))
