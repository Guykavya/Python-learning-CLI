# Red, green: which version passes what?

Here is a TDD session in miniature. The test file `test_calc.py` stays the same. The file
`calc.py` is replaced by four versions of `max_of`, one after the other. For each version, say
what the last line of `python -m pytest -q` shows.

```python
import pytest

from calc import max_of


def test_picks_the_biggest():
    assert max_of([3, 1, 2]) == 3


def test_single_item():
    assert max_of([5]) == 5


def test_negative_numbers():
    assert max_of([-4, -2, -9]) == -2


def test_empty_list_raises():
    with pytest.raises(ValueError):
        max_of([])


def test_biggest_is_last():
    assert max_of([1, 2, 9]) == 9
```

Version 1:

```python
def max_of(numbers):
    return 0
```

Version 2:

```python
def max_of(numbers):
    return numbers[0]
```

Version 3:

```python
def max_of(numbers):
    best = 0
    for n in numbers:
        if n > best:
            best = n
    return best
```

Version 4:

```python
def max_of(numbers):
    if not numbers:
        raise ValueError("empty list")
    best = numbers[0]
    for n in numbers:
        if n > best:
            best = n
    return best
```

Write one line per version, `version N: ` followed by the summary exactly as pytest prints it
(without the time), for example `version 5: 2 failed, 3 passed`. When all tests pass, pytest prints
just `5 passed`.
