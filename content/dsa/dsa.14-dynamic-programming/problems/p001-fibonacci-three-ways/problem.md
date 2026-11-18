# Fibonacci three ways

The Fibonacci numbers are `F(0) = 0`, `F(1) = 1` and `F(n) = F(n - 1) + F(n - 2)`. Chapter sections 1, 3 and 4 compute them in three ways. Write all three, in one file:

1. `fib_naive(n)`: the plain recursion, with no memory at all.
2. `fib_memo(n)`: the same recursion **plus a notebook** (a `memo` dictionary or `functools.cache`). Top-down.
3. `fib_table(n)`: a list `f` of size `n + 1`, filled from small `i` to large. Bottom-up, **no recursion**.

## Example

```python
>>> [fib_naive(n) for n in range(10)]
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
>>> fib_memo(90)
2880067194370816120
>>> fib_table(100)
354224848179261915075
>>> len(str(fib_table(5000)))      # a 1045-digit number: Python ints never overflow
1045
```

## Constraints

- `fib_naive(n)` is only tested for `n <= 25` (it makes about 240,000 calls for 25).
- `fib_memo(n)` is tested up to `n = 700`, in a fresh Python, under a time limit. Without the notebook it would take longer than the age of the universe.
- `fib_table(n)` is tested up to `n = 5000`. A recursion 5000 deep crashes Python (chapter section 3, trap 2); a table does not recurse at all.

## Think about

Write down the three parts of the recipe (chapter section 2) once: state, transition, base case. All three functions share them. What changes between the three versions is only **how the answers to smaller questions are remembered**.
