## Approach

A decorator with arguments is a function that **makes** a decorator. `repeat(n)` checks `n` and returns
`decorate`. `decorate(func)` returns `wrapper`. `wrapper` sees both `n` and `func` through closures and
collects `n` results.

## Code

```python
from functools import wraps


def repeat(n):
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")

    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(n):
                results.append(func(*args, **kwargs))
            return results
        return wrapper

    return decorate
```

## Complexity

Each call runs `func` n times: O(n) calls and an O(n) list.

## Another way

`return [func(*args, **kwargs) for _ in range(n)]` in one line does the same. Checking `n` inside the
wrapper would also "work", but the mistake would show up only at the first call, far from the line that
caused it. Fail as early as you can.
