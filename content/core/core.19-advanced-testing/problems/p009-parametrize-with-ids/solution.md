## Approach

One function, one table. Each row is `(a, b, c, expected)` and has a name. Rows are added for
every region where a different bug lives: sides in other positions, boundary of the triangle
inequality, non-positive sides.

## Code

```python
import pytest

from target import triangle_kind


@pytest.mark.parametrize(
    "a, b, c, expected",
    [
        (3, 3, 3, "equilateral"),
        (3, 3, 4, "isosceles"),
        (3, 4, 3, "isosceles"),
        (4, 3, 3, "isosceles"),
        (3, 4, 5, "scalene"),
        (1, 2, 3, "invalid"),
        (0, 1, 1, "invalid"),
        (-1, 2, 2, "invalid"),
        (2, 2, 5, "invalid"),
        (5, 2, 2, "invalid"),
    ],
    ids=["equilateral", "iso-first-two", "iso-first-last", "iso-last-two", "scalene",
         "flat-line", "zero-side", "negative-side", "iso-too-short", "long-first-side"],
)
def test_kind(a, b, c, expected):
    assert triangle_kind(a, b, c) == expected, f"({a}, {b}, {c}) should be {expected}"
```

## Cost

Each row is reported as its own test (`test_kind[flat-line]`), so one failing row does not hide
the others, and `pytest -k flat-line` runs just that row.

## Another way

`pytest.param(3, 4, 5, "scalene", id="scalene")` puts the id next to its row, so ids and rows
cannot get out of step. Stack two `parametrize` decorators to get every combination (a cross
product).
