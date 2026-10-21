## Approach

`count` is a local of `make_counter`, captured in a cell by the inner `counter`. `nonlocal count`
tells Python that `count += step` should rebind that enclosing variable instead of creating a
new local. Each call of `make_counter` creates a new cell, so counters are independent.

## Code

```python
def make_counter(start=0, step=1):
    """Return a function that adds step to a private count and returns it."""
    count = start

    def counter():
        nonlocal count
        count += step
        return count

    return counter
```

## Complexity

O(1) per call.

## Another way

Keep the count in a one-item list, `box = [start]`, and do `box[0] += step` inside. Mutation needs
no `nonlocal`. This was the usual trick before `nonlocal` existed; `nonlocal` says what you mean.
