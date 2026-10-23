# Which test catches which bug?

This is the assessed trace for the module. It shows how the checker of the "write tests"
problems thinks: a test suite is good if every plausible bug makes **some** test fail.

The correct function is `fee(minutes)` for a car park: the first 30 minutes are free, then 10
for every **started** hour, never more than 100 per day, and a negative time is an error.

```python
def fee(minutes):
    if minutes < 0:
        raise ValueError("minutes cannot be negative")
    if minutes <= 30:
        return 0
    extra = minutes - 30
    hours = (extra + 59) // 60
    return min(hours * 10, 100)
```

This is the test file `test_parking.py` (it imports `fee` from `parking.py`):

```python
import pytest

from parking import fee


def test_free_half_hour():
    assert fee(30) == 0


def test_zero_minutes():
    assert fee(0) == 0


def test_just_over_free_time():
    assert fee(31) == 10


def test_exact_hour_after_free_time():
    assert fee(90) == 10


def test_next_started_hour():
    assert fee(91) == 20


def test_daily_cap():
    assert fee(1440) == 100


def test_negative_time():
    with pytest.raises(ValueError):
        fee(-5)
```

Below are six versions of `parking.py`: five have **one small bug** each; version F is the
correct function above. Predict, for each version, which tests **fail**.

Version A:

```python
def fee(minutes):
    if minutes < 0:
        raise ValueError("minutes cannot be negative")
    if minutes <= 30:
        return 0
    extra = minutes - 29
    hours = (extra + 59) // 60
    return min(hours * 10, 100)
```

Version B:

```python
def fee(minutes):
    if minutes < 0:
        raise ValueError("minutes cannot be negative")
    if minutes <= 30:
        return 0
    extra = minutes - 30
    hours = extra // 60
    return min(hours * 10, 100)
```

Version C:

```python
def fee(minutes):
    if minutes < 0:
        raise ValueError("minutes cannot be negative")
    if minutes <= 30:
        return 0
    extra = minutes - 30
    hours = (extra + 59) // 60
    return hours * 10
```

Version D:

```python
def fee(minutes):
    if minutes <= 30:
        return 0
    extra = minutes - 30
    hours = (extra + 59) // 60
    return min(hours * 10, 100)
```

Version E:

```python
def fee(minutes):
    if minutes < 0:
        raise ValueError("minutes cannot be negative")
    if minutes <= 31:
        return 0
    extra = minutes - 30
    hours = (extra + 59) // 60
    return min(hours * 10, 100)
```

Write one line per version: `version X: ` followed by the names of the failing tests, in the
order they appear in the file, separated by `, `. If no test fails write `version X: all pass`.
Work through the arithmetic by hand: for each version and each test, compute what `fee(...)`
returns. Remember that `pytest.raises` fails when nothing is raised.
