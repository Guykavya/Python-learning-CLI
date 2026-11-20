# Read the constraints

Before you write any code in a contest, you read the **constraints** and decide how slow your algorithm may be. CPython does roughly `10**7` simple operations per second (one loop step, one addition, one comparison). A time limit of `s` seconds therefore gives you a budget of `10**7 * s` operations.

Seven complexity classes, from fastest to slowest, and what each one costs for an input of size `n`:

| Class | Operations |
|---|---|
| `log n` | `log2(n)` |
| `n` | `n` |
| `n log n` | `n * log2(n)` |
| `n sqrt n` | `n * sqrt(n)` |
| `n^2` | `n * n` |
| `n^3` | `n * n * n` |
| `2^n` | `2 ** n` |

A class is **allowed** when its operation count is at most the budget. Print the **slowest allowed class** (the one furthest down the table). Because `log n` costs at most about 30 operations here, at least one class is always allowed.

## Input

The first line holds `t`, the number of test cases. Each of the next `t` lines holds two integers `n` and `s`: the input size and the time limit in seconds (`1 <= n <= 10**9`, `1 <= s <= 10`).

## Output

For each case print the name of the slowest allowed class, exactly as written in the table.

## Example

```text
3
100000 1
1000000 1
20 1
```
```text
n log n
n
2^n
```

For `n = 10**5` and one second the budget is `10**7`. `n log n` costs about `1.7 * 10**6` (allowed), `n sqrt n` costs about `3.2 * 10**7` (too much), so the answer is `n log n`. For `n = 20`, `2**20` is about `10**6`, so even `2^n` fits.
