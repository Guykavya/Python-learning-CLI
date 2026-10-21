## Approach

Two base cases: a non-container is depth 0, and a container with no items is depth 1 (the loop
does not run, `deepest` stays 0). Otherwise the depth is one more than the deepest item, found by
recursing on every item and keeping the maximum.

## Code

```python
def depth(data):
    """Return the nesting depth of lists and tuples in data (0 for non-containers)."""
    if not isinstance(data, (list, tuple)):
        return 0
    deepest = 0
    for item in data:
        deepest = max(deepest, depth(item))
    return 1 + deepest
```

## Complexity

O(total number of items) time; recursion depth equals the nesting depth.

## Another way

With a generator expression and `max`'s `default` (core.04):
`return 1 + max((depth(item) for item in data), default=0)`.
