# Trace: a counter above or below lru_cache

The same two decorators, `counted` and `lru_cache`, are stacked in two orders on the same
recursive function. A third version decorates without the `@` syntax. Predict the exact output.

Three facts to keep in mind:

- The recursive call `fib_a(n - 1)` looks up the **global name** `fib_a` when it runs.
- `functools.wraps` (and `lru_cache`, which uses the same machinery) copies the wrapped function's
  `__dict__`, so attributes such as `calls` are **copied** to the new wrapper at decoration time.
- `__wrapped__` gives you the function one layer down.

```python
from functools import lru_cache, wraps


def counted(func):
    @wraps(func)
    def wrapper(*args):
        wrapper.calls += 1
        return func(*args)
    wrapper.calls = 0
    return wrapper


@counted
@lru_cache(maxsize=None)
def fib_a(n):
    return n if n < 2 else fib_a(n - 1) + fib_a(n - 2)


@lru_cache(maxsize=None)
@counted
def fib_b(n):
    return n if n < 2 else fib_b(n - 1) + fib_b(n - 2)


def plain(n):
    return n if n < 2 else plain(n - 1) + plain(n - 2)


counted_plain = counted(plain)

print(fib_a(5), fib_a.calls)
print(fib_a(5), fib_a.calls)
print(fib_a.__wrapped__.cache_info())
print(fib_b(5), fib_b.__wrapped__.calls)
print(fib_b(5), fib_b.__wrapped__.calls)
print(fib_b.cache_info())
print(counted_plain(5), counted_plain.calls)
print(fib_b.__name__, fib_b.calls)
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
