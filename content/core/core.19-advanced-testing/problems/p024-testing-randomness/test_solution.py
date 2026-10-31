import random

import pytest

from solution import draw_winners, roll_dice

NAMES = ["a", "b", "c", "d", "e", "f"]


def test_draw_winners_matches_a_seeded_reference():
    got = draw_winners(NAMES, 3, random.Random(7))
    assert got == random.Random(7).sample(NAMES, 3), (
        "Use rng.sample(entries, k) on the generator you were given.")


def test_same_seed_same_result():
    assert draw_winners(NAMES, 3, random.Random(1)) == draw_winners(NAMES, 3, random.Random(1))
    assert roll_dice(5, random.Random(1)) == roll_dice(5, random.Random(1)), (
        "The same seed must give the same dice.")


def test_roll_dice_matches_a_seeded_reference():
    ref = random.Random(11)
    expected = [ref.randint(1, 6) for _ in range(4)]
    assert roll_dice(4, random.Random(11)) == expected, (
        "Draw rng.randint(1, 6) once per die, in order.")


def test_entries_are_not_changed_and_result_is_new():
    entries = list(NAMES)
    result = draw_winners(entries, 2, random.Random(3))
    assert entries == NAMES, "draw_winners must not change the list it was given (do not shuffle in place)."
    assert result is not entries


def test_winners_are_distinct_members():
    result = draw_winners(NAMES, 6, random.Random(5))
    assert sorted(result) == NAMES, "Drawing all k = len(entries) gives every entry exactly once."


def test_invalid_arguments():
    for k in (-1, 7):
        with pytest.raises(ValueError):
            draw_winners(NAMES, k, random.Random(0))
    with pytest.raises(ValueError):
        roll_dice(-1, random.Random(0))
    assert draw_winners(NAMES, 0, random.Random(0)) == []
    assert roll_dice(0, random.Random(0)) == []


def test_global_random_state_is_untouched():
    random.seed(123)
    before = random.getstate()
    draw_winners(NAMES, 3, random.Random(1))
    roll_dice(5, random.Random(1))
    draw_winners(NAMES, 3)
    roll_dice(5)
    assert random.getstate() == before, (
        "Never use the module-level random functions: use the rng you were given (or random.Random()).")


def test_default_generator_gives_valid_results():
    dice = roll_dice(200)
    assert len(dice) == 200 and set(dice) <= {1, 2, 3, 4, 5, 6}, "Dice are integers from 1 to 6."
    assert len(set(dice)) > 1, "Without an rng the dice must still be random, not constant."
    assert len(draw_winners(NAMES, 2)) == 2
