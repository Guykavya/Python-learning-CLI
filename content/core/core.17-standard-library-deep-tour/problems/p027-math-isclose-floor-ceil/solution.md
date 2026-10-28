## Approach

- `floor`, `ceil` and `trunc` agree for positive numbers and differ for negative ones: `floor(-2.5)`
  is `-3` (down), `trunc(-2.5)` is `-2` (towards zero, like `int()`).
- Ceiling division of integers: `a // b` floors, so `-(-a // b)` floors the negative and flips it
  back, which is the ceiling. It never leaves the integers, so it is exact for any size;
  `math.ceil(a / b)` goes through a float and breaks above about 2**53.
- Rounding down to a step means "floor of how many steps fit", times the step: `floor(x / step) * step`.
- `math.isclose(a, b, rel_tol, abs_tol)` is true if `abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)`.
  `rel_tol` scales with the size of the numbers (good for `1e10`); `abs_tol` is needed near zero.

## Code

```python
import math


def floor_ceil_trunc(x: float) -> tuple[int, int, int]:
    return math.floor(x), math.ceil(x), math.trunc(x)


def pages_needed(n_items: int, per_page: int) -> int:
    if per_page <= 0 or n_items < 0:
        raise ValueError("per_page must be positive and n_items not negative")
    return -(-n_items // per_page)


def round_down_to(x: float, step: float) -> float:
    if step <= 0:
        raise ValueError("step must be positive")
    return math.floor(x / step) * step


def close_enough(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
```

## Complexity

All O(1) for normal numbers (integer division of huge ints is proportional to their length).

## Another way

`(n_items + per_page - 1) // per_page` is the other common integer ceiling division. `divmod`
also works: `q, r = divmod(n_items, per_page); return q + (r > 0)`. For money, avoid floats
entirely: count in cents (ints) or use `decimal.Decimal`, and `round_down_to` becomes exact.
