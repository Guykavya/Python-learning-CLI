## Approach

State: `f(i, j)` is True when the first `i + j` letters of `s3` are an interleaving of `s1[:i]` and `s2[:j]`. We never need a third index for `s3`: it is fixed by `i + j`, so there are only `(n + 1) * (m + 1)` states.

Transition: the last letter of `s3[:i + j]` came from one of the two strings.

- From `s1`: `s1[i - 1] == s3[i + j - 1]` and `f(i - 1, j)`.
- From `s2`: `s2[j - 1] == s3[i + j - 1]` and `f(i, j - 1)`.

Base: `f(0, 0) = True`. Answer: `f(n, m)`, after checking the lengths.

```python
def is_interleave(s1, s2, s3):
    n, m = len(s1), len(s2)
    if n + m != len(s3):
        return False
    f = [[False] * (m + 1) for _ in range(n + 1)]
    f[0][0] = True
    for i in range(n + 1):
        for j in range(m + 1):
            if i > 0 and f[i - 1][j] and s1[i - 1] == s3[i + j - 1]:
                f[i][j] = True
            if j > 0 and f[i][j - 1] and s2[j - 1] == s3[i + j - 1]:
                f[i][j] = True
    return f[n][m]
```

The guards `i > 0` and `j > 0` handle the first row and column inside the same loop, so there is no separate base-case loop to get wrong.

## Complexity

`O(n * m)` time and memory; `O(m)` memory with one rolling row (each cell needs the cell above and the cell to its left).

## Another way

Top-down with `@functools.cache`: `go(i, j)` returns True if `s3[i + j:]` is an interleaving of `s1[i:]` and `s2[j:]`. Try "take `s1[i]`" and "take `s2[j]`" when they match `s3[i + j]`. Without the cache it is exponential: on `"a" * 300`, `"a" * 300` and `"a" * 599 + "b"` every split of the a's is tried before the `b` says no. With the cache there are at most `301 * 301` states, and the recursion depth is at most 600.
