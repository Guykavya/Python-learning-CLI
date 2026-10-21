## Approach

The base case `n == 0` answers directly. The recursive case trusts `factorial(n - 1)` to be
correct and multiplies by `n`. Each call shrinks `n` by one, so every chain of calls reaches 0.

## Code

```python
def factorial(n):
    """Return n! for n >= 0, computed recursively."""
    if n == 0:
        return 1
    return n * factorial(n - 1)
```

## Complexity

O(n) calls and O(n) stack depth. Fine for n up to several hundred; beyond about 1000 the recursion limit is hit.

## Another way

A loop, `result = 1; for k in range(2, n + 1): result *= k`, uses constant stack space and works
for any n. `math.factorial(n)` is the built-in.
