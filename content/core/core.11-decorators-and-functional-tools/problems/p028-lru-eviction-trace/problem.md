# Trace: lru_cache with a small maxsize

With `maxsize=2` the cache holds at most two results. When a third one must go in, the cache
throws out the **least recently used** entry: the one that was not used (stored **or** read)
for the longest time.

Two more facts you need:

- The cache key is built from the arguments **as you wrote them**. A call by position and a
  call by keyword build different keys, even if they mean the same thing.
- `cache_info()` reports `hits`, `misses`, `maxsize` and `currsize` (how many entries are stored now).

Predict the exact output.

```python
from functools import lru_cache


@lru_cache(maxsize=2)
def square(n):
    print(f"compute {n}")
    return n * n


print(square(2))
print(square(3))
print(square(2))
print(square(4))
print(square(3))
print(square(2))
print(square.cache_info())
square.cache_clear()
print(square(4))
print(square(n=4))
print(square(4))
print(square.cache_info())
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
