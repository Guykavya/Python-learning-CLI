## Approach

A common supersequence must contain every letter of `a` and every letter of `b`. A letter can serve **both** strings only if the shared letters form a common subsequence. So the most letters we can share is the LCS, and the shortest length is `len(a) + len(b) - LCS(a, b)`.

To build one, walk the LCS table back from the corner, like `lcs_string` in section 14, but **write every letter you pass**: a matched letter once, and on a step up or left the letter of the string you step along. When one string is used up, copy what is left of the other.

```python
def lcs_table(a, b):
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1] + 1
            else:
                f[i][j] = max(f[i - 1][j], f[i][j - 1])
    return f


def shortest_supersequence(a, b):
    f = lcs_table(a, b)
    i, j = len(a), len(b)
    out = []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])            # shared letter: written once
            i -= 1
            j -= 1
        elif f[i - 1][j] >= f[i][j - 1]:
            out.append(a[i - 1])            # a[i-1] is not shared on this path
            i -= 1
        else:
            out.append(b[j - 1])
            j -= 1
    while i > 0:
        out.append(a[i - 1])
        i -= 1
    while j > 0:
        out.append(b[j - 1])
        j -= 1
    return "".join(reversed(out))
```

For `"abac"` and `"cab"` (LCS `"ab"`), the walk starts at `(4, 3)`: `c` vs `b` differ, the upper neighbour is larger, so it writes `c` from `a` and steps up; `a` vs `b` differ, it writes `a` and steps up; `b` = `b`, it writes the shared `b`; `a` = `a`, it writes the shared `a`; now `i = 0`, so the leftover `c` of `b` is written. Collected backwards: `c a b a c`, reversed `"cabac"`. Why is the walk shortest? Every step writes exactly one letter. A diagonal step consumes a letter of both strings; the walk follows the larger neighbour, so it makes exactly `LCS(a, b)` diagonal steps, and the total is `len(a) + len(b) - LCS`.

## Complexity

`O(n * m)` time and memory for the table, plus `O(n + m)` for the walk.

## Another way

Top-down: `scs(i, j)` = a shortest supersequence of `a[i:]` and `b[j:]`, with `@functools.cache`. If `a[i] == b[j]` it is `a[i] + scs(i+1, j+1)`; else the shorter of `a[i] + scs(i+1, j)` and `b[j] + scs(i, j+1)`. It is correct, but it stores a whole string per state, so it uses `O(n * m * (n + m))` memory, and the recursion depth is `n + m`. Storing only lengths and rebuilding afterwards, as above, is the standard fix.
