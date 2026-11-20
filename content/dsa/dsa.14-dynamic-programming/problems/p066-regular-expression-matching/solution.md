## Approach

State: `f(i, j)` is True when `s[:i]` matches `p[:j]`. Look at the end of the pattern prefix.

- `p[j-1]` is a letter or `.`: it must match `s[i-1]`, and the rest must match: `f(i-1, j-1)`.
- `p[j-1]` is `*`: the last unit is `x*` with `x = p[j-2]`. Either it is used **zero** times, `f(i, j-2)`, or it matches **one more** character: `s[i-1]` matches `x` and the unit is still there for what comes before: `f(i-1, j)`.

As in p065, "one more and stay" (keep `j`, move `i`) covers every count with a single read. Base: `f(0, 0) = True`; in the first row only units `x*` can match the empty string, `f(0, j) = f(0, j-2)` when `p[j-1] == '*'`.

```python
def same(c, pc):
    return pc == "." or pc == c


def is_match(s, p):
    n, m = len(s), len(p)
    f = [[False] * (m + 1) for _ in range(n + 1)]
    f[0][0] = True
    for j in range(2, m + 1):
        if p[j - 1] == "*":
            f[0][j] = f[0][j - 2]                 # every x* so far is empty
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == "*":
                f[i][j] = f[i][j - 2] or (same(s[i - 1], p[j - 2]) and f[i - 1][j])
            else:
                f[i][j] = same(s[i - 1], p[j - 1]) and f[i - 1][j - 1]
    return f[n][m]
```

Check `"aab"` against `"c*a*b"`: the first row is `True, False, True, False, True, False` (`""` matches `""`, `"c*"` and `"c*a*"`). Row `a`: `c*a*` matches `"a"` through "one more `a`" from the first row. Row `aa`: the same again. Row `aab`: `b` matches `b` and `f(2, 4)` (`"aa"` against `"c*a*"`) is True.

## Complexity

`O(n * m)` time and memory.

## Another way

Top-down, which many find easier to write: `go(i, j)` = does `s[i:]` match `p[j:]`, with `@functools.cache`. Let `first = i < len(s) and same(s[i], p[j])`. If `p[j + 1] == '*'`: `go(i, j + 2) or (first and go(i + 1, j))`; else `first and go(i + 1, j + 1)`. Without the cache this is the backtracking that real regex engines do, and it explodes on the input in the constraints: the tests show it.
