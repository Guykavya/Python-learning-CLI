## Approach

Each function does one of four standard jobs, and each job has a standard tool:

1. Numbering items: `enumerate(lines, start=1)` gives `(1, 'a'), (2, 'b'), ...`.
2. Walking two lists together: `zip(a, b)` pairs items and stops at the shorter list, which is
   exactly what the old `if i < len(b)` test did by hand.
3. "Is there any ...?": `any(...)` with a generator expression. It stops at the first `True`.
   The old loop kept going to the end for nothing.
4. Counting matches: `sum(x == y for ...)`; `True` counts as 1.

## Code

```python
def indexed_lines(lines):
    return [f"{n}: {line}" for n, line in enumerate(lines, start=1)]


def add_lists(a, b):
    return [x + y for x, y in zip(a, b)]


def has_negative(numbers):
    return any(n < 0 for n in numbers)


def count_equal_positions(a, b):
    return sum(x == y for x, y in zip(a, b))
```

## Complexity

All four are O(n) time. `has_negative` can stop early. Memory is O(1) except for the two
functions that build a list. Bonus: the new versions accept any iterable (generators, strings),
because they never call `len` or index.

## Another way

`add_lists` with `map`: `list(map(operator.add, a, b))`. `has_negative` with `min`:
`min(numbers, default=0) < 0` (works, but cannot stop early and reads less clearly).
`indexed_lines` with a plain loop and `enumerate` also passes.
