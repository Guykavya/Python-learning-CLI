## Approach

`p` is a period exactly when `s[:n - p] == s[p:]`, which says that the prefix of length `n - p` is a suffix too: a **border** of length `b = n - p`. So the periods are `n - b` for the borders `b` of `s`, including the empty border (period `n`).

- Smallest period: the longest border, `n - pi[n - 1]` (chapter section 11).
- All periods: walk the chain of borders `pi[n - 1]`, `pi[b - 1]`, ..., down to 0. Shorter borders give larger periods, so the list comes out increasing.

```python
def prefix_function(s):
    pi = [0] * len(s)
    k = 0
    for i in range(1, len(s)):
        while k > 0 and s[i] != s[k]:
            k = pi[k - 1]
        if s[i] == s[k]:
            k += 1
        pi[i] = k
    return pi


def all_periods(s):
    n = len(s)
    pi = prefix_function(s)
    periods = []
    b = pi[-1]                       # the longest border
    while b > 0:
        periods.append(n - b)        # a border of length b gives the period n - b
        b = pi[b - 1]                # the next shorter border
    periods.append(n)                # the empty border: period n
    return periods


def smallest_period(s):
    return len(s) - prefix_function(s)[-1]
```

`aabaa`: the borders are `aa` (2) and `a` (1), so the periods are 3, 4 and 5. The period 4 is not a multiple of 3: periods of a string with a cut-short last block do not have to be multiples of the smallest one.

## Complexity

`O(n)` for the prefix function; the border chain has at most `n` steps. `O(n)` memory.

## Another way

With the Z-function (p021): `p` is a period exactly when `z[p] == n - p` (for `p < n`). Loop over `p` and collect them: also `O(n)`.
