# Write tests: parametrize with ids

Copy-pasting a test and changing two numbers is a smell: a bug in the copy goes unnoticed and
every new case adds six lines. **`@pytest.mark.parametrize`** turns the copies into one test
plus a table, and **`ids=`** gives every row a name that shows up in the failure report.

The code under test:

```python
def triangle_kind(a, b, c):
    """Name the triangle with sides a, b, c: 'equilateral', 'isosceles', 'scalene' or 'invalid'."""
    if min(a, b, c) <= 0 or a + b <= c or a + c <= b or b + c <= a:
        return "invalid"
    if a == b == c:
        return "equilateral"
    if a == b or a == c or b == c:
        return "isosceles"
    return "scalene"
```

The `starter.py` has three copy-pasted tests. In `solution.py` replace them by **one**
parametrized test function (at most two test functions in total) so that

- it **passes** on the code above,
- it **fails** on each of seven buggy versions (the checker names the survivor),
- there are **at least nine rows** in the table, and
- every row has a readable name, with `ids=[...]` or `pytest.param(..., id="...")`.

Save the code above as `target.py` next to your `solution.py` and run
`python -m pytest solution.py` to try your tests. Give every `assert` a message.

**Example**

```python
import pytest

@pytest.mark.parametrize(
    "a, b, c, expected",
    [(3, 3, 3, "equilateral"), (3, 4, 5, "scalene")],
    ids=["all-equal", "all-different"],
)
def test_kind(a, b, c, expected):
    assert triangle_kind(a, b, c) == expected, f"({a}, {b}, {c}) should be {expected}"
```
