## Hint 1

Do the single-value lines first (`A` to `E`). For each, ask whether the value's type is the declared type or a "smaller" type that is accepted in its place (`int` for `float`, `bool` for `int`).

## Hint 2

`F` and `G` both make a `list[float]` out of ints, but `F` is a **literal** (mypy builds it as `list[float]` right there) while `G` reuses an existing `list[int]` variable. Which one could break the other list's promise?

## Hint 3

For the tuples: `(1, 2)` for `tuple[float, ...]` is fine (ints fit floats), but is `2.5` an `int`? For the dicts, check each value against the declared **value** type: `1` for `float`, `1.5` for `int`.
