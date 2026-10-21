## Approach

`*steps` collects any number of functions, and because `collect` comes after it, `collect` can
only be passed by keyword. Thread the value through the steps, recording each intermediate value
in case the caller asked for them.

## Code

```python
def run_pipeline(value, *steps, collect=False):
    """Pass value through each step left to right; return the result, or every value if collect."""
    history = [value]
    for step in steps:
        value = step(value)
        history.append(value)
    if collect:
        return history
    return value
```

## Complexity

One call per step; O(k) extra space for the history.

## Another way

`functools.reduce(lambda acc, step: step(acc), steps, value)` computes the final value in one
line, but it cannot easily record the history.
