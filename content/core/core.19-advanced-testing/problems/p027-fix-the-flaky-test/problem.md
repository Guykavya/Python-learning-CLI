# Fix the flaky test

The test file in `solution.py` passes on Kavya's laptop in the morning and sometimes fails in CI. It
fails when run alone, fails when run in a different order, and it fails on other days. The code under
test is fine; the **tests** are the problem. This is the code (saved as `target.py`):

```python
import random
from datetime import datetime

_events = []


def current_hour():
    return datetime.now().hour


def greeting():
    """'Good morning' before 12:00, 'Good afternoon' from 12:00 to 17:59, otherwise 'Good evening'."""
    hour = current_hour()
    if hour < 12:
        return "Good morning"
    if hour < 18:
        return "Good afternoon"
    return "Good evening"


def unique_tags(tags):
    """Return the distinct tags as a list. The order of the result is not specified."""
    return list(set(tags))


def roll_dice(count, rng=None):
    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""
    rng = rng or random
    return [rng.randint(1, 6) for _ in range(count)]


def record(event):
    """Remember an event and return how many events are stored now."""
    _events.append(event)
    return len(_events)


def events():
    """Return a copy of the stored events, oldest first."""
    return list(_events)


def clear():
    """Forget all events."""
    _events.clear()
```

**Symptoms** (no causes given, find them yourself):

- `python -m pytest solution.py -p no:cacheprovider` is green in the morning and red after lunch.
- `python -m pytest solution.py -k next_record` fails; so does running the tests in reverse order.
- Two runs of the same command on the same afternoon sometimes differ.
- `PYTHONHASHSEED=1 python -m pytest solution.py` and `PYTHONHASHSEED=2 python -m pytest solution.py`
  do not agree.

Edit `solution.py` so the suite is **deterministic**: it must pass every time, in any order, with any
hash seed, at any hour, and with unseeded random numbers. You must also keep the suite **useful**:
the checker runs it against ten buggy versions of `target.py` (wrong greeting borders, duplicates,
wrong dice range, off-by-one counts, and more), and each must still be caught.

Rules: keep at least 5 test functions; do not use `skip`, `xfail` or `sleep`.

**How this is checked.** `solution.py` starts as the flaky file. The checker copies it next to
`target.py` and runs real pytest many times on the correct code, each time with a different shuffled
test order, `PYTHONHASHSEED`, and pretended current hour; all runs must pass. Then it runs your tests
against buggy copies of `target.py`; each must fail.
