## Approach

Apply the conversion recipe of chapter section 4 to `go(i, run)`:

1. **Memo to table:** `t[i][run]` for `i` in `0..n` and `run` in `0..k-1` (a run of `k` is never stored, because it is forbidden).
2. **Base cases first:** `go(0, run) = 1`, so the whole row `t[0]` is ones.
3. **Calls to reads:** `go(i - 1, 0)` is `t[i - 1][0]`, `go(i - 1, run + 1)` is `t[i - 1][run + 1]`.
4. **Order:** row `i` reads only row `i - 1`, so `i` goes up; the `run` order is free.
5. **Answer:** the cell the first call asked for, `t[n][0]`.

```python
def count_strings(n, k):
    t = [[0] * k for _ in range(n + 1)]
    for run in range(k):
        t[0][run] = 1                                  # base case: nothing left to place
    for i in range(1, n + 1):
        for run in range(k):
            total = t[i - 1][0]                        # place a 0
            if run + 1 < k:
                total += t[i - 1][run + 1]             # place a 1
            t[i][run] = total
    return t[n][0]
```

## Complexity

`(n + 1) * k` cells, each `O(1)` work: `O(n * k)` time and space. For `n = 5000, k = 50`, that is 250,000 cells, filled in a fraction of a second.

## Another way

Each row reads only the previous one, so two rows are enough (chapter section 6):

```python
def count_strings(n, k):
    prev = [1] * k
    for _ in range(n):
        prev = [prev[0] + (prev[run + 1] if run + 1 < k else 0) for run in range(k)]
    return prev[0]
```

Or build strings **forwards**: `g[i][run]` = the number of strings of length `i` that end in `run` ones; then add up the last row. Different table, same answer. The top-down code also works if you warm its cache from the bottom (call `go(100, 0)`, `go(200, 0)`, ... first), but that keeps the recursion and its limit; the table removes it.
