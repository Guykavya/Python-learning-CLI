## Approach

Each guard is a decorator factory. The wrapper looks at `args` first and raises if something is wrong;
only then does it call `func`. With stacking, `typed` is on top, so it is the outer wrapper and checks types
first; `in_range` then checks values. Both use `@wraps(func)`, so the inner wrapper already carries the
name `add_marks`, and the outer one copies it again.

## Code

```python
from functools import wraps


def typed(*types):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = func.__name__
            if len(args) != len(types):
                raise TypeError(f"{name}() expects {len(types)} positional arguments, got {len(args)}")
            for i, (arg, wanted) in enumerate(zip(args, types), start=1):
                if not isinstance(arg, wanted):
                    raise TypeError(
                        f"{name}() argument {i} must be {wanted.__name__}, got {type(arg).__name__}"
                    )
            return func(*args, **kwargs)
        return wrapper
    return decorate


def in_range(low, high):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i, arg in enumerate(args, start=1):
                if isinstance(arg, (int, float)) and not (low <= arg <= high):
                    raise ValueError(f"{func.__name__}() argument {i} = {arg} is outside {low}..{high}")
            return func(*args, **kwargs)
        return wrapper
    return decorate
```

## Complexity

O(k) extra work per call for k positional arguments.

## Another way

You could write the checks at the top of each function. That repeats code and is easy to forget. The
decorators keep one copy of the rule. Note one Python detail: `bool` is a subclass of `int`, so
`isinstance(True, int)` is `True` and `typed(int)` accepts `True`. If that matters, check
`type(arg) is wanted` instead.
