**1. What `@` means.** The lines

```python
@log_calls
def total(prices): ...
```

are the same as defining `total` normally and then writing `total = log_calls(total)`. This runs once, at
**definition time**, when Python executes the `def`. So `decorating total` prints as soon as the module
loads, before `total` is ever called. `calling total` prints on every call, because that line is inside the
wrapper.

**2. What `total` points to.** `log_calls` returns `wrapper`, and that object is stored under the name
`total`. The original function still exists, but only `wrapper` can reach it, through the closure variable
`func`. So `total.__name__` is the name of the wrapper's `def`: `wrapper`. Its docstring is `None` because
the inner `def wrapper` has no docstring.

**3. What `wraps` does.** `functools.wraps(func)` is a decorator that goes on the inner function:
`@wraps(func)` on the line above `def wrapper`. It copies `__name__`, `__qualname__`, `__doc__`,
`__module__` and the attribute dict `__dict__` from `func` to `wrapper`, and it sets
`wrapper.__wrapped__ = func`, so the original can still be reached. It does not change what the wrapper does.

**4. Why it matters.** Without it, every decorated function looks like `wrapper`. `help(total)` shows no
docstring. Log lines and error reports that print `func.__name__` all say `wrapper`, so you cannot tell which
function failed. A registry that stores handlers by `f.__name__` puts them all under the same key, so they
overwrite each other. A second decorator stacked on top reads the wrong name. Test tools that list function
names become useless. One line, `@wraps(func)`, fixes all of this.
