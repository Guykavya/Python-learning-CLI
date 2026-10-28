# Explain: what @ really does, and why wraps matters

Ravi wrote a logging decorator and used it on a function:

```python
def log_calls(func):
    print("decorating", func.__name__)
    def wrapper(*args, **kwargs):
        print("calling", func.__name__)
        return func(*args, **kwargs)
    return wrapper


@log_calls
def total(prices):
    """Add up a list of prices."""
    return sum(prices)


print(total([10, 20]))
print(total.__name__)   # wrapper
print(total.__doc__)    # None
```

He asks: "What does the `@` line actually do? Why does `total.__name__` say `wrapper`, and where did my
docstring go? Does it matter?"

In `answer.md` (about 150 to 300 words), explain:

1. What `@log_calls` above `def total` is **equivalent to**, written as one ordinary assignment line,
   and **when** that line runs (definition time or call time). Say when `decorating total` is printed.
2. After decoration, which function object does the name `total` point to? Use that to explain why
   `__name__` is `wrapper` and `__doc__` is `None`.
3. What `functools.wraps` does, and **where** in the code it goes. Name at least three things it copies or sets.
4. Two concrete problems that a missing `wraps` causes in real code (for example `help()`, logs, a registry
   keyed by `__name__`, a second decorator that reads `__name__`, test reports).
