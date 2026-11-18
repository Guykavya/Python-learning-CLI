## Approach

The table of chapter section 15:

- State: `f[i][j]` = edit distance between `a[:i]` and `b[:j]`.
- Base: `f[i][0] = i`, `f[0][j] = j`.
- Transition: equal last characters cost nothing, `f[i-1][j-1]`; otherwise `1 + min(replace f[i-1][j-1], delete f[i-1][j], insert f[i][j-1])`.

Each row only reads the row above and the cell to its left, so two rows are enough (chapter section 15, "Rolling arrays"):

```python
def edit_distance(a, b):
    prev = list(range(len(b) + 1))               # row 0: f[0][j] = j inserts
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)                 # f[i][0] = i deletes
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1]             # keep it, no cost
            else:
                cur[j] = 1 + min(prev[j - 1],    # replace
                                 prev[j],        # delete a[i-1]
                                 cur[j - 1])     # insert b[j-1]
        prev = cur
    return prev[-1]
```

Why are these three moves enough? At the end of an optimal alignment, either the last characters are lined up (equal, or one replace), or `a`'s last character was deleted, or `b`'s last character was inserted. Nothing else can happen to them. The equal case needs no `min`: keeping an equal character is never worse.

## Complexity

`O(n * m)` time, `O(m)` space with two rows (`O(n * m)` with the full table).

## Another way

Top-down with `functools.cache` on `(i, j)`, with the same base cases (`i == 0` returns `j`, `j == 0` returns `i`). It is a direct copy of the definition. Without the cache, every mismatch makes three calls, and two strings of length 400 never finish.
