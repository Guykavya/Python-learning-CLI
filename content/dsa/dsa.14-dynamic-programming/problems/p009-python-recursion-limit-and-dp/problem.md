# Python recursion limit and DP

Start from a positive integer `n`. In one move you may:

- subtract 1, or
- divide by 2, if the number is even, or
- divide by 3, if the number is divisible by 3.

Write `min_steps(n)` that returns the **fewest moves** to reach 1.

Here is a correct top-down solution. Run it in your head for `n = 10**4`:

```python
import functools

@functools.cache
def min_steps_memo(n):
    if n == 1:
        return 0
    best = min_steps_memo(n - 1) + 1
    if n % 2 == 0:
        best = min(best, min_steps_memo(n // 2) + 1)
    if n % 3 == 0:
        best = min(best, min_steps_memo(n // 3) + 1)
    return best

min_steps_memo(10**4)       # RecursionError: maximum recursion depth exceeded
```

The algorithm is fine (it has `n` states and constant work each). The **recursion depth** is not: `min_steps_memo(n - 1)` is asked first, so the call chain goes `n, n - 1, n - 2, ..., 1`, about `n` frames deep, and Python stops at about 1000 (chapter section 3, trap 2).

Your `min_steps(n)` must work for `n` up to `2 * 10**5` **with Python's normal recursion limit**. Use one of the cures of chapter section 3: a table (best), or warming the cache from the bottom.

## Example

```python
>>> min_steps(1)
0
>>> min_steps(10)          # 10 -> 9 -> 3 -> 1 (greedy "divide when you can" does 10 -> 5 -> 4 -> 2 -> 1)
3
>>> min_steps(10**4)
14
```

## Constraints

- `1 <= n <= 2 * 10**5`.
- Do not change the recursion limit. A recursion 200,000 deep can crash the Python interpreter itself, not only raise an error.

## Think about

`f(i)` depends on `f(i - 1)`, `f(i // 2)` and `f(i // 3)`: all **smaller** numbers. So what order fills a table safely? Is greedy ("divide by 3 if you can, else by 2, else subtract") good enough? Try `n = 10`.
