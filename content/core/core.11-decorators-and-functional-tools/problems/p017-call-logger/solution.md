## Approach

The factory receives the list; the wrapper closes over it and appends to it. The call text is built once
from `repr` of each positional argument and `key=repr(value)` for each keyword (a dict keeps the caller's
order). The call runs inside `try`: on an error we log the error type and re-raise it unchanged; on success
we log `-> repr(result)` and return the result.

## Code

```python
from functools import wraps


def logged(log):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            parts = [repr(a) for a in args]
            parts += [f"{key}={value!r}" for key, value in kwargs.items()]
            call = f"{func.__name__}({', '.join(parts)})"
            try:
                result = func(*args, **kwargs)
            except Exception as error:
                log.append(f"{call} raised {type(error).__name__}")
                raise
            log.append(f"{call} -> {result!r}")
            return result
        return wrapper
    return decorate
```

## Complexity

O(size of the arguments and result) per call, for building the text.

## Another way

Pass a function instead of a list: `logged(write)` and call `write(line)`. Then the same decorator can write
to a list in tests (`write=log.append`) and to the screen in the program (`write=print`). This is the same
"inject what you need" idea as the timer problem.
