## Approach

State: `f(i, j)` is True when the prefix `s[:i]` matches the pattern prefix `p[:j]`. Transition on the last pattern character:

| `p[j-1]` | `f(i, j)` | why |
|---|---|---|
| letter `c` | `s[i-1] == c and f(i-1, j-1)` | both last characters are used |
| `?` | `i > 0 and f(i-1, j-1)` | `?` eats exactly one character |
| `*` | `f(i, j-1) or f(i-1, j)` | the star is empty, or it eats `s[i-1]` and stays |

The star case is the heart of the problem. "The star eats one more letter" keeps `j` and moves `i`: the same star can then eat another letter in the next cell up. That is how one cell with two reads covers every length of the star.

Base: `f(0, 0) = True`; the first row `f(0, j)` is True while the pattern so far has only stars; the first column `f(i, 0)` is False for `i > 0`.

```python
def wildcard_match(s, p):
    n, m = len(s), len(p)
    f = [[False] * (m + 1) for _ in range(n + 1)]
    f[0][0] = True
    for j in range(1, m + 1):
        f[0][j] = f[0][j - 1] and p[j - 1] == "*"       # only stars can match ""
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if p[j - 1] == "*":
                f[i][j] = f[i][j - 1] or f[i - 1][j]     # empty, or eat s[i-1] and stay
            elif p[j - 1] == "?" or p[j - 1] == s[i - 1]:
                f[i][j] = f[i - 1][j - 1]
    return f[n][m]
```

Check `"adceb"` with `"*a*b"`: the first `*` is empty, `a` matches `a`, the second `*` eats `d`, `c`, `e` one cell at a time (moving down its column), and `b` matches `b`.

## Complexity

`O(n * m)` time and memory, `O(m)` with two rows.

## Another way

There is a famous greedy with backtracking to the **last** star only: walk both strings; on a mismatch, go back to the most recent `*` and let it eat one more character. It runs in `O(n * m)` in the worst case and `O(1)` memory, and it is correct for wildcards because a later star can always absorb what an earlier one would have eaten. It does **not** carry over to regular expressions (problem p066), where `x*` only repeats one character; the DP does.
