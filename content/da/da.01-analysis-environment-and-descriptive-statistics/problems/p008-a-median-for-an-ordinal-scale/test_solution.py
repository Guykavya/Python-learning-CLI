import random

import pytest

from solution import ordinal_median

ORDER = ["strongly disagree", "disagree", "neutral", "agree", "strongly agree"]


def test_odd_count():
    assert ordinal_median(["agree", "disagree", "neutral"], ORDER) == "neutral", "Sort by the scale order, not alphabetically; the middle of 3 is 'neutral'."


def test_odd_count_not_alphabetical():
    got = ordinal_median(["agree", "agree", "strongly disagree"], ORDER)
    assert got == "agree", "Alphabetical order would put 'agree' first; use the position in `order`."


def test_even_count_different_middles():
    got = ordinal_median(["agree", "agree", "neutral", "disagree"], ORDER)
    assert got == ("neutral", "agree"), "Even count, middle labels differ: return (lower, upper) as a tuple."


def test_even_count_same_middles():
    got = ordinal_median(["agree", "agree", "agree", "neutral"], ORDER)
    assert got == "agree", "If both middle labels are the same, return that label, not a tuple."


def test_single_response():
    assert ordinal_median(["neutral"], ORDER) == "neutral", "One response is its own median."


def test_unknown_label():
    with pytest.raises(ValueError, match="maybe"):
        ordinal_median(["agree", "maybe"], ORDER)


def test_empty():
    with pytest.raises(ValueError):
        ordinal_median([], ORDER)


def test_no_mutation_and_random_against_a_slow_version():
    for seed in range(20):
        rng = random.Random(seed)
        data = [rng.choice(ORDER) for _ in range(rng.randint(1, 15))]
        copy = list(data)
        got = ordinal_median(data, ORDER)
        assert data == copy, "Do not reorder the caller's list."
        ranks = sorted(ORDER.index(x) for x in data)
        n = len(ranks)
        if n % 2:
            want = ORDER[ranks[n // 2]]
        else:
            lo, hi = ORDER[ranks[n // 2 - 1]], ORDER[ranks[n // 2]]
            want = lo if lo == hi else (lo, hi)
        assert got == want, f"Wrong median for {sorted(data, key=ORDER.index)}: expected {want}."
