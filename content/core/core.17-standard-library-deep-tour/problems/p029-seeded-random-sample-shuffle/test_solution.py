import random

import pytest

from solution import pick_winners, roll_dice, shuffled, split_data

NAMES = ["Asha", "Ben", "Chen", "Dev", "Esha", "Farah"]


# ------------------------------------------------------------------ exact values (Mersenne Twister, fixed by the seed)
def test_shuffled_exact():
    assert shuffled([1, 2, 3, 4, 5, 6, 7, 8], 42) == [4, 5, 7, 8, 3, 6, 1, 2], (
        "Use random.Random(seed).shuffle(copy). Any other call order (or the global random functions after "
        "other calls) gives a different order."
    )
    assert shuffled(list("abcde"), 2024) == ["a", "e", "c", "b", "d"], "Same recipe, another seed."


def test_pick_winners_exact():
    assert pick_winners(NAMES, 3, 42) == ["Farah", "Asha", "Esha"], (
        "Use random.Random(seed).sample(names, k): it picks k DIFFERENT names. choices() can repeat a name."
    )
    assert pick_winners(NAMES, 3, 7) == ["Chen", "Ben", "Dev"], "Another seed, another fixed result."


def test_roll_dice_exact():
    assert roll_dice(10, 42) == [6, 1, 1, 6, 3, 2, 2, 2, 6, 1], (
        "Make ONE Random(seed) and call rng.randint(1, 6) n times. Creating a new Random(seed) for each roll "
        "would give the same number every time."
    )


def test_split_data_exact():
    train, test = split_data(list(range(10)), 30, 42)
    assert (train, test) == ([8, 5, 6, 9, 4, 0, 1], [7, 3, 2]), (
        "Shuffle a copy with shuffled(items, seed); the FIRST len * test_percent // 100 items are the test part, "
        "the rest is the training part. Return (train, test) in that order."
    )
    assert split_data(list(range(7)), 50, 3) == ([6, 5, 4, 1], [0, 2, 3]), "7 * 50 // 100 = 3 test items (integer division)."


# ------------------------------------------------------------------ properties
def test_same_seed_same_result_every_call():
    assert shuffled(list(range(20)), 5) == shuffled(list(range(20)), 5), (
        "The same seed must give the same order on every call: create a new Random(seed) inside the function, "
        "not one shared generator at module level."
    )
    assert roll_dice(5, 9) == roll_dice(5, 9), "roll_dice must be repeatable too."


def test_different_seeds_differ():
    assert shuffled(list(range(20)), 1) != shuffled(list(range(20)), 2), "Different seeds should (almost always) give different orders."


def test_shuffled_does_not_change_input():
    items = [1, 2, 3, 4, 5]
    out = shuffled(items, 42)
    assert items == [1, 2, 3, 4, 5], "shuffle() works in place: shuffle a COPY, not the caller's list."
    assert sorted(out) == items and out is not items, "Return a new list with the same items."


def test_pick_winners_distinct_and_bad_k():
    w = pick_winners(NAMES, 6, 1)
    assert sorted(w) == sorted(NAMES), "With k = len(names) every name is picked exactly once."
    with pytest.raises(ValueError):
        pick_winners(NAMES, 7, 1)  # sample() refuses k larger than the population


def test_roll_dice_range():
    rolls = roll_dice(600, 123)
    assert set(rolls) == {1, 2, 3, 4, 5, 6}, "randint(1, 6) includes BOTH ends: values 1 to 6. randrange(1, 6) would never give 6."


def test_split_data_edges():
    train, test = split_data([1, 2, 3], 0, 1)
    assert test == [] and train == shuffled([1, 2, 3], 1), "0% test: everything is training data (still shuffled)."
    train, test = split_data(list(range(10)), 100, 4)
    assert train == [] and sorted(test) == list(range(10)), "100% test: everything is test data."
    with pytest.raises(ValueError):
        split_data([1, 2], 101, 1)


def test_global_random_state_is_untouched():
    random.seed(99)
    expected = [random.random() for _ in range(3)]
    random.seed(99)
    shuffled(list(range(10)), 1)
    pick_winners(NAMES, 2, 1)
    roll_dice(5, 1)
    split_data(list(range(10)), 20, 1)
    assert [random.random() for _ in range(3)] == expected, (
        "Your functions changed the GLOBAL random generator (random.seed / random.shuffle ...). Other code that "
        "uses random would suddenly change. Use your own random.Random(seed) object."
    )
