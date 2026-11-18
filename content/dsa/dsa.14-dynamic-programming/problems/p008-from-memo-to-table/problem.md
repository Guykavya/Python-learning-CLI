# From memo to table

How many binary strings of length `n` have **no run of `k` ones in a row**? A colleague wrote a correct top-down DP:

```python
import functools

def count_strings_memo(n, k):
    @functools.cache
    def go(i, run):
        # i   = characters still to place
        # run = how many 1s the string ends with right now (always < k)
        if i == 0:
            return 1                       # base case: one finished string
        total = go(i - 1, 0)               # place a 0: the run of ones is broken
        if run + 1 < k:
            total += go(i - 1, run + 1)    # place a 1: allowed only if the run stays below k
        return total

    return go(n, 0)
```

It works for small `n`, but `go(5000, 0)` is 5000 calls deep and raises `RecursionError`. Rewrite it **bottom-up**: write `count_strings(n, k)` that fills a table `t[i][run]` with loops and **no recursion**, and returns the same answers.

## Example

```python
>>> count_strings(4, 3)        # 16 strings minus 0111, 1110, 1111
13
>>> [count_strings(n, 2) for n in range(8)]     # no "11": a Fibonacci pattern
[1, 2, 3, 5, 8, 13, 21, 34]
>>> count_strings(5, 1)        # no 1 at all: only "00000"
1
>>> count_strings(0, 3)        # the empty string
1
```

## Constraints

- `0 <= n <= 5000`, `1 <= k <= 50`. Return the exact count (an int with up to about 1500 digits).
- **No recursion.** The test runs `n = 5000` with Python's normal recursion limit.

## Think about

Follow the conversion recipe of chapter section 4, one step at a time: what is the size of the table in each dimension (`i` from 0 to `n`, `run` from 0 to `k - 1`)? Which cells are the base case? `go(i, ...)` reads `go(i - 1, ...)`: so in which direction must the `i` loop run? Does the order of the `run` loop matter?
