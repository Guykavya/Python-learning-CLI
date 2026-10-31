## Approach

A test is flaky when its result depends on something the test does not control. Four sources here:

1. **Time.** `greeting()` reads the real hour. Replace `current_hour` with `monkeypatch.setattr` and
   test the borders 11/12 and 17/18.
2. **Set order.** `unique_tags` returns `list(set(...))` and the order of a set of strings changes with
   `PYTHONHASHSEED`. Compare `sorted(...)`, or `set(...)`, because the order is not part of the promise.
3. **Randomness.** `6 in roll_dice(6)` fails one run in three. Pass a seeded `random.Random` and check
   range, length and the exact sequence.
4. **Shared state / order.** `record` uses a module-level list. Tests that rely on what a previous test
   left behind break when the order changes. An `autouse` fixture resets the state around every test.

A fix must not remove the checks (the mutants make sure of it).

## Code

```python
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
    assert greeting() == expected


def test_unique_tags_removes_duplicates():
    assert sorted(unique_tags(["python", "testing", "python", "tdd"])) == ["python", "tdd", "testing"]
    assert unique_tags([]) == []


def test_roll_dice_count_and_range():
    rolls = roll_dice(600, random.Random(1))
    assert len(rolls) == 600
    assert set(rolls) == {1, 2, 3, 4, 5, 6}


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
```

## Complexity

Not applicable.

## Another way

Instead of an `autouse` fixture, give `target` a class (`EventLog`) and create a new object in each
test: then there is no module-level state to reset. Inject a clock into `greeting(hour)` the same way.

## How to hunt flakiness

Run the suite with the order reversed or shuffled, with several `PYTHONHASHSEED` values, and a few
times in a row. A flaky test shows its cause when you change one outside factor at a time.
