# One test function, many rows: what is reported?

With `@pytest.mark.parametrize` pytest makes one test per row and names each one
`function_name[id]`. The id is built from the values, joined by `-`; floats and negative numbers
print as written, and `ids=[...]` replaces the generated text. This is `test_table.py`:

```python
import pytest


@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (2.5, 0.5, 3.0),
])
def test_add(a, b, expected):
    assert a + b == expected


@pytest.mark.parametrize("word", ["level", "abc", "noon"])
def test_palindrome(word):
    assert word == word[::-1]


@pytest.mark.parametrize("n", [1, 2], ids=["one", "two"])
def test_positive(n):
    assert n > 1


@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", ["a", "b"])
def test_pair(x, y):
    assert str(x) + y != "2b"
```

Predict what `python -m pytest -v` reports. Write one line for every test, **in the order pytest
runs them**, as `name[id] PASSED` or `name[id] FAILED`, and finish with the summary line
(`N failed, M passed`).

Hints for the tricky one: when two `parametrize` decorators are stacked, pytest makes every
combination, the **bottom** decorator's value comes first in the id, and the values of the
**bottom** decorator also vary slowest (the top one changes fastest).
