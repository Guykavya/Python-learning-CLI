import random
import statistics

import pytest

from solution import best_centre, total_loss


def test_total_loss_by_hand():
    assert total_loss([1, 2, 6], 3, "squared") == 14, "Squared: (1-3)**2 + (2-3)**2 + (6-3)**2 = 4 + 1 + 9."
    assert total_loss([1, 2, 6], 2, "absolute") == 5, "Absolute: |1-2| + |2-2| + |6-2| = 1 + 0 + 4."


def test_unknown_kind():
    with pytest.raises(ValueError):
        total_loss([1, 2], 1, "cubic")
    with pytest.raises(ValueError):
        best_centre([1, 2], "huber")


def test_empty():
    with pytest.raises(ValueError):
        best_centre([], "squared")


def test_squared_loss_is_minimised_by_the_mean():
    got = best_centre([1, 2, 6], "squared")
    assert got == pytest.approx(3.0, rel=1e-9), "The mean (3.0) is not a data value: include it among the candidates."


def test_absolute_loss_is_minimised_by_the_median():
    assert best_centre([1, 2, 6], "absolute") == 2, "For absolute loss the median (2) wins; the mean (3) is worse."


@pytest.mark.parametrize("seed", range(15))
def test_random_lists(seed):
    rng = random.Random(seed)
    data = [rng.randint(-30, 60) for _ in range(rng.randint(1, 25))]
    sq = best_centre(data, "squared")
    assert sq == pytest.approx(statistics.fmean(data), rel=1e-9, abs=1e-9), f"Squared loss: the best centre is the mean, got {sq}."
    ab = best_centre(data, "absolute")
    want = total_loss(data, statistics.median(data), "absolute")
    assert total_loss(data, ab, "absolute") == pytest.approx(want, rel=1e-9), "Absolute loss at your centre must equal the loss at the median (any point between the two middle values is fine for an even count)."
    for _ in range(20):
        c = rng.uniform(min(data) - 5, max(data) + 5)
        assert total_loss(data, sq, "squared") <= total_loss(data, c, "squared") + 1e-9, "Another point has a smaller squared loss than yours."


def test_even_length_tie_goes_to_the_smaller_candidate():
    assert best_centre([1, 2, 3, 4], "absolute") == 2, "2 and 3 tie (loss 4); on a tie return the smaller one."
