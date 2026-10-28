# What does lru_cache remember?

`lru_cache` stores each result by its arguments. A call with arguments it has seen is a **hit** and does
not run the body. A new call is a **miss** and runs the body. Predict the exact output, including
every `CacheInfo(...)` line.

```python
from functools import lru_cache


@lru_cache(maxsize=None)
def fib(n):
    print("compute", n)
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


print(fib(4))
print(fib.cache_info())
print(fib(5))
print(fib.cache_info())
print(fib(3))
print(fib.cache_info())
fib.cache_clear()
print(fib(1))
print(fib.cache_info())
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
