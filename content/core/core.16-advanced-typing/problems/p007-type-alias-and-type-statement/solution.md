## Approach

`type Name = <type>` creates a **type alias object** (a `typing.TypeAliasType`). Its right-hand side is evaluated lazily, only when something asks for it. That laziness is why the alias may mention itself: `Json` appears in its own definition, which an ordinary assignment `Json = dict[str, Json] | ...` could not do (`NameError`: `Json` does not exist yet when the right side runs). Type checkers read it as a recursive type, so `count_leaves` can walk any depth.

`Point` and `Matrix` are ordinary aliases; they only shorten the hints. `count_leaves` follows the shape of the type: a `dict` is the sum over its values, a `list` the sum over its items, everything else is a leaf worth 1. A `str` is **not** iterated: it falls into the leaf case.

## Code

```python
import math

type Point = tuple[float, float]
type Matrix = list[list[float]]
type Json = dict[str, Json] | list[Json] | str | int | float | bool | None


def distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def scale(m: Matrix, k: float) -> Matrix:
    return [[x * k for x in row] for row in m]


def count_leaves(value: Json) -> int:
    if isinstance(value, dict):
        return sum(count_leaves(v) for v in value.values())
    if isinstance(value, list):
        return sum(count_leaves(v) for v in value)
    return 1
```

## Complexity

`distance` O(1); `scale` O(rows x columns); `count_leaves` O(n) in the number of nodes (recursion depth = nesting depth).

## Another way

Before Python 3.12: `Point: TypeAlias = tuple[float, float]` (with `from typing import TypeAlias`). A recursive alias then needs a string for the inner name: `Json: TypeAlias = "dict[str, Json] | list[Json] | str | ..."`. The `type` statement is cleaner and also lets an alias be generic: `type Pair[T] = tuple[T, T]`.
