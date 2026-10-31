## Hint 1

Where should the number live so that each decorated function has its own? The wrapper is a new object for
every decorated function. Can you put an attribute on it right after you define it?

## Hint 2

Increase the counter first, then call the original, so a call that raises is still counted.

```
def count_calls(func):
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper
```
