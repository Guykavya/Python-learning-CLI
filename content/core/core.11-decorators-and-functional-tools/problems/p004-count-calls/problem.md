# @count_calls: state on the wrapper

Functions are objects, so you can store an attribute on them: `wrapper.calls = 0`.
Use this to count how often a decorated function is called.

Write the decorator `count_calls(func)` in `solution.py`:

- It returns a wrapper that accepts any arguments (`*args, **kwargs`) and passes them on to `func`.
- The wrapper returns whatever `func` returns.
- The wrapper has an attribute `calls`. It is `0` right after decoration and goes up by 1 on **every** call,
  also on a call where `func` raises an error.
- Each decorated function has its own counter.

Then use it with the `@` syntax on a function `square(n)` that returns `n * n`.

**Example**

```python
@count_calls
def square(n):
    return n * n

square.calls      # 0
square(3)         # 9
square(4)         # 16
square.calls      # 2
```
