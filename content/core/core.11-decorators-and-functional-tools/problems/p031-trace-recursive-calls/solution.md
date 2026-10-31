## Approach

`depth` lives in the closure of `decorator`, so each decorated function has its own. Every call
saves its own `indent` in a local variable before going deeper. That local copy is what makes the
`->` line line up with its call line, even after many nested calls changed `depth`.

`finally` is the safe place for `depth -= 1`: it runs after a normal return **and** after an
exception. Without it, one exception would leave the depth too high for ever.

Why are the recursive calls traced at all? `fact(n - 1)` inside the body looks up the global
name `fact` when that line runs. The decorator replaced that name with the wrapper, so every
inner call goes through the wrapper too. That is also why `fact.__wrapped__(3)` still traces
`fact(2)` and below: only the first call skipped the wrapper.

## Code

```python
from functools import wraps


def trace_calls(log):
    def decorator(func):
        depth = 0

        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal depth
            indent = "  " * depth
            parts = [repr(a) for a in args]
            parts += [f"{k}={v!r}" for k, v in kwargs.items()]
            log.append(f"{indent}{func.__name__}({', '.join(parts)})")
            depth += 1
            try:
                result = func(*args, **kwargs)
            except Exception as err:
                log.append(f"{indent}!! {type(err).__name__}")
                raise
            finally:
                depth -= 1
            log.append(f"{indent}-> {result!r}")
            return result
        return wrapper
    return decorator
```

## Complexity

O(1) extra work per call plus the cost of `repr` of the arguments. The log grows by two lines per call.

## Another way

Store the depth as a function attribute, `wrapper.depth`, instead of `nonlocal`. Then a test
can look at `fact.depth` after an exception and check that it is back to 0.

The same "the recursive call goes through the decorated name" rule is what makes `@lru_cache`
on `fib` fast: the inner calls also hit the cache.
