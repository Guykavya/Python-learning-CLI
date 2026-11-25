import numpy as np
import pytest

from solution import best_of_many_optimism


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_the_winner_looks_skilful_on_validation(seed):
    val, test = best_of_many_optimism(300, seed)
    assert val > 0.58, f"best-of-300 validation accuracy {val:.2f}: the maximum of 300 coin-flip-like scores on 100 rows is far above 0.5."


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_but_it_is_a_coin_on_fresh_data(seed):
    val, test = best_of_many_optimism(300, seed)
    assert 0.44 < test < 0.56, f"test accuracy {test:.2f} should be about 0.5: the labels are pure noise. Score the winner on the TEST data."
    assert val - test > 0.05, "the optimism (validation minus test) must be clearly positive for the best of 300."


def test_one_model_has_little_optimism_on_average():
    gaps = [np.subtract(*best_of_many_optimism(1, s)) for s in range(40)]
    assert abs(np.mean(gaps)) < 0.03, "with a single candidate there is no selection: the average gap is about 0."


def test_more_models_more_optimism():
    few = np.mean([best_of_many_optimism(5, s)[0] for s in range(10)])
    many = np.mean([best_of_many_optimism(200, s)[0] for s in range(10)])
    assert many > few + 0.05, "the best validation accuracy grows with the number of candidates tried."


def test_reproducible():
    assert best_of_many_optimism(20, 7) == best_of_many_optimism(20, 7), "one default_rng(seed): same seed, same answer."
