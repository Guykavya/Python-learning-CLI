# Fibonacci with a memo dictionary

Write `fib(n)` that returns the n-th Fibonacci number (`fib(0) = 0`, `fib(1) = 1`, `fib(n) = fib(n-1) + fib(n-2)`), recursively, **with memoisation**: store every answer in a dictionary the first time you compute it, and look it up when the same `n` comes again (chapter section 4).

The plain version makes about 1.6 times more calls for every step of `n`. Yours must compute `fib(300)` at once.

Use a dictionary, not `functools.cache` (the point is to see how a memo works).

## Example

```python
>>> fib(10)
55
>>> fib(300)
222232244629420445529739893461909967206666939096499764990979600
```

## Constraints

- `0 <= n <= 500`
- Calls with different `n` in a row must all give correct results.

## Think about

Where does the memo live? A dictionary created **inside** `fib` at every call is useless (each call gets a new, empty one). Put it outside the recursive function: a module-level dictionary, or an inner helper function that shares one dictionary.
