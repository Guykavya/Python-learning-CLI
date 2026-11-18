## Approach

The table of chapter section 14:

- State: `f[i][j]` = LCS length of `a[:i]` and `b[:j]`.
- Transition: equal last characters are matched, `f[i-1][j-1] + 1`; otherwise drop the last character of `a` or of `b`, `max(f[i-1][j], f[i][j-1])`.
- Base: row 0 and column 0 are 0.

```python
def lcs_length(a, b):
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]     # f[i][j]: LCS of a[:i] and b[:j]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1] + 1      # match the last characters
            else:
                f[i][j] = max(f[i - 1][j], f[i][j - 1])
    return f[n][m]
```

Matching equal last characters at once is safe (chapter section 14): if a longest common subsequence used neither, adding the match would make it longer; if it used one of them, it can use the other equal character instead.

## Complexity

`O(n * m)` time and space. Only the length is needed, so two rows are enough: `O(min(n, m))` space (chapter section 14, "Two rows are enough").

## Another way

Top-down with `functools.cache`: `lcs(i, j)` on the prefixes with the same three cases. The recursion depth can reach `len(a) + len(b)` (800 here), close to Python's limit of 1000, which is one reason the table is preferred for long strings. Without the cache, every mismatch splits into two calls: exponential.
