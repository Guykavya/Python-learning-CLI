## Approach

A **0/1 knapsack with two capacities** (chapter section 10). Each string is an item that weighs `z` zeros and `o` ones and is worth 1. The state needs both remaining capacities:

- State: `f[i][j]` = the most strings, among those processed so far, that fit in `i` zeros and `j` ones.
- Transition for the next string: `f[i][j] = max(f[i][j], f[i - z][j - o] + 1)` if it fits.
- Base: all 0. Answer: `f[m][n]`.

The full version would be 3-D (`strings x zeros x ones`). Row `k` only reads row `k - 1`, so one 2-D table updated in place is enough, as with the 1-D knapsack array. And as there, the capacity loops go **from high to low** so that `f[i - z][j - o]` has not yet been updated for this string.

```python
def find_max_form(strs, m, n):
    f = [[0] * (n + 1) for _ in range(m + 1)]   # f[i][j]: at most i zeros, j ones
    for s in strs:
        z = s.count("0")
        o = s.count("1")
        for i in range(m, z - 1, -1):           # both loops downwards: each string once
            row, prev = f[i], f[i - z]
            for j in range(n, o - 1, -1):
                if prev[j - o] + 1 > row[j]:
                    row[j] = prev[j - o] + 1
    return f[m][n]
```

Why must **both** loops go down? When `z = 0` (a string like `"11"`), `prev` *is* `row`, and only the `j` direction protects the old value. When `o = 0` (like `"00"`), only the `i` direction does. With either loop upwards, `["0"]` with `m = 3` would be counted 3 times.

`row, prev = f[i], f[i - z]` is only a speed-up: it saves two index lookups in the inner loop.

## Complexity

`O(L * m * n)` time for `L` strings (plus counting characters), `O(m * n)` space. For 300 strings and `m = n = 60`: about a million steps.

## Another way

Top-down: `best(k, i, j)` = the most strings from index `k` on, with `i` zeros and `j` ones left; leave the string or (if it fits) take it. With `functools.cache` there are `L * (m + 1) * (n + 1)` states, a few million here: it works, but uses much more memory and time than the table. Without the cache it is `2**L`.
