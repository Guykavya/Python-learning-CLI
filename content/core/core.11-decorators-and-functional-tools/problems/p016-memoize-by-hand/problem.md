# @memoize by hand, with keyword arguments

`functools.cache` is ready to use, but writing it yourself shows how it works. Write the decorator
`memoize(func)` in `solution.py`:

- The wrapper keeps a dict from "the arguments of a call" to "the result of that call". If the same
  arguments come again, return the stored result **without** calling `func`.
- The key must include keyword arguments, and their **order must not matter**: `f(a=1, b=2)` and
  `f(b=2, a=1)` are the same call. Build the key as `(args, tuple(sorted(kwargs.items())))`.
- A stored result of `None` (or `0`, or `""`) is still a stored result. Do not call `func` again for it.
- If `func` raises, store nothing, so the next call tries again.
- Expose the dict as `wrapper.cache`, and keep the metadata with `functools.wraps`.

You may assume all arguments are hashable.

**Example**

```python
@memoize
def slow_square(n):
    print("computing", n)
    return n * n

slow_square(4)    # prints "computing 4", returns 16
slow_square(4)    # returns 16, prints nothing
len(slow_square.cache)   # 1
```

Because `@memoize` replaces the name, a recursive function calls the memoized version of itself:

```python
@memoize
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

fib(80)   # 23416728348467685, instantly
```
