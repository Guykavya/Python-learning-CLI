## Approach

**Grades.** `bisect_right(breakpoints, score)` returns how many breakpoints are `<= score`,
which is exactly "how many grade boundaries this score has passed". That number is the index into
`"FDCBA"`. `bisect_right` (not `bisect_left`) is what makes a score equal to a breakpoint count as
passing it: for 60, `bisect_right` gives 1 (D), `bisect_left` would give 0 (F).

**Range count.** In a sorted list, the items `>= lo` start at `bisect_left(a, lo)`, and the items
`<= hi` end just before `bisect_right(a, hi)`. The difference is the count. The `lo > hi` guard
avoids a negative answer.

## Code

```python
from bisect import bisect_left, bisect_right


def grade(score: int, breakpoints: list[int] = [60, 70, 80, 90], grades: str = "FDCBA") -> str:
    return grades[bisect_right(breakpoints, score)]


def count_in_range(sorted_nums: list[int], lo: int, hi: int) -> int:
    if lo > hi:
        return 0
    return bisect_right(sorted_nums, hi) - bisect_left(sorted_nums, lo)
```

## Complexity

Both are O(log n) per call. A loop or an `if/elif` chain is O(n) in the number of bands or items.

## Another way

`grade` is the example from the `bisect` documentation. The table-driven idea also works with a
plain loop over `zip(breakpoints, grades)`, which is fine for five grades. For counting,
`sum(lo <= n <= hi for n in a)` is correct and simple, but O(n) per query: with a million numbers
and many queries, bisect wins by far. A tuple default like `breakpoints=(60, 70, 80, 90)` would
make the "never modified" promise explicit.
