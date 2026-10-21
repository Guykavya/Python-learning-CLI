## Approach

A closure stores `func`, the tuple `args` and the dict `kwargs`. On each call, the new function
builds the full argument list: stored positionals then new ones, and a **new** merged keyword dict
in which call-time keywords win. Building a new dict each time is essential: updating the stored
one would make an override permanent.

## Code

```python
def partial_apply(func, *args, **kwargs):
    """Return g where g(*more, **more_kw) == func(*args, *more, **(kwargs | more_kw))."""
    def g(*more_args, **more_kwargs):
        merged = kwargs | more_kwargs
        return func(*args, *more_args, **merged)
    return g
```

## Complexity

O(number of arguments) per call, plus the cost of `func`.

## Another way

`functools.partial(func, *args, **kwargs)` is the library version, with the same merging rule. It
also exposes `.func`, `.args` and `.keywords` attributes, which a closure does not.
