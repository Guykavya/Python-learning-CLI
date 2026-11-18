## Approach

State: `f(i, j)` = the number of ways to pick `t[:j]` as a subsequence of `s[:i]`.

Transition, on the last letter `s[i-1]`:

- every way that does **not** use it: `f(i-1, j)`;
- if `s[i-1] == t[j-1]`, every way that matches it with the last letter of `t`: `f(i-1, j-1)`.

The two groups do not overlap (one uses position `i-1`, the other does not), so we add them. Base: `f(i, 0) = 1`, `f(0, j) = 0` for `j > 0`.

```python
def num_distinct(s, t):
    n, m = len(s), len(t)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        f[i][0] = 1                              # empty t: one way
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            f[i][j] = f[i - 1][j]                # do not use s[i-1]
            if s[i - 1] == t[j - 1]:
                f[i][j] += f[i - 1][j - 1]       # use s[i-1] for t[j-1]
    return f[n][m]
```

Note the difference from LCS: when the letters are equal, the LCS takes **only** the diagonal (matching is never worse). Here we count, so we must **also** count the ways that skip the letter: `"rabbbit"` has three `b`s that can each play the last `b` of `"rabbit"`.

## Complexity

`O(n * m)` time and memory.

## Another way

Each row only needs the row above, so one list is enough (section 6), if `j` goes **downwards**: `f[j - 1]` must still hold the value of the previous row when `f[j]` is updated.

```python
def num_distinct(s, t):
    f = [1] + [0] * len(t)
    for ch in s:
        for j in range(len(t), 0, -1):          # downwards, like the 0/1 knapsack
            if t[j - 1] == ch:
                f[j] += f[j - 1]
    return f[len(t)]
```

With `j` going upwards, one letter of `s` could be used twice: `num_distinct("a", "aa")` would give 1 instead of 0. This is the same trap as the 1-D 0/1 knapsack in section 10.
