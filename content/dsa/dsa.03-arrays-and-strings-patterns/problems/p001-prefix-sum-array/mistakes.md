- Forgetting the leading `0`. Then the list has `n` cells, and later range-sum formulas need `if l == 0` special cases.
  With `p[0] = 0` the sum of `a[l..r]` is always `p[r+1] - p[l]`.
- Computing each cell with `sum(a[:i])`. Every cell re-adds everything before it: O(n^2), far too slow for 200000.
- Printing the list itself: `print(p)` shows brackets and commas. Use `print(*p)`.
- Crashing on `n = 0`. `input().split()` on an empty line gives `[]`, which is fine; just do not index `a[0]`.
