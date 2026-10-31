import random

import pytest

import target
from target import events, greeting, record, roll_dice, unique_tags


@pytest.fixture(autouse=True)
def clean_events():
    target.clear()
    yield
    target.clear()


@pytest.mark.parametrize("hour, expected", [
    (0, "Good morning"), (11, "Good morning"),
    (12, "Good afternoon"), (17, "Good afternoon"),
    (18, "Good evening"), (23, "Good evening"),
])
def test_greeting_for_each_part_of_the_day(monkeypatch, hour, expected):
    monkeypatch.setattr(target, "current_hour", lambda: hour)
    assert greeting() == expected, f"At {hour}:00 the greeting must be {expected!r}."


def test_unique_tags_removes_duplicates():
    assert sorted(unique_tags(["python", "testing", "python", "tdd"])) == ["python", "tdd", "testing"], (
        "Compare in a fixed order: the order of unique_tags is not specified.")
    assert unique_tags([]) == []


def test_roll_dice_count_and_range():
    rolls = roll_dice(600, random.Random(1))
    assert len(rolls) == 600
    assert set(rolls) == {1, 2, 3, 4, 5, 6}, "600 seeded dice use every face from 1 to 6, and only those."


def test_roll_dice_uses_the_given_rng():
    reference = random.Random(5)
    assert roll_dice(4, random.Random(5)) == [reference.randint(1, 6) for _ in range(4)]


def test_events_are_kept_in_order():
    record("x")
    record("y")
    assert events() == ["x", "y"]


def test_record_returns_the_number_of_events():
    assert record("a") == 1
    assert record("b") == 2


def test_clear_forgets_everything():
    record("a")
    target.clear()
    assert events() == []
