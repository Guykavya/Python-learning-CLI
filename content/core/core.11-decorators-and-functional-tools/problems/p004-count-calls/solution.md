## Approach

The wrapper is a function object, so it can carry an attribute. Set `wrapper.calls = 0` once, when
decorating. Inside the wrapper, the name `wrapper` is found in the enclosing function, so
`wrapper.calls += 1` updates the attribute on that same object. Count before calling `func`, so a call
that raises is still counted. Each call of `count_calls` creates a new wrapper, so each decorated
function gets its own counter.

## Code

```python
def count_calls(func):
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper


@count_calls
def square(n):
    return n * n
```

## Complexity

O(1) extra work per call.

## Another way

Keep the count in a closure variable with `nonlocal count` and `count += 1`. That works too, but then the
outside world cannot read it. Storing it on the wrapper makes `square.calls` visible to tests and callers.
