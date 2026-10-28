## Hint 1

`functools.wraps(func)` is itself a decorator (a decorator with an argument). Which function should it
decorate: `func` or `wrapper`?

## Hint 2

```
from functools import wraps

def strip_result(func):
    @wraps(func)                 # copy func's name, doc, ... onto wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).strip()
    return wrapper
```
