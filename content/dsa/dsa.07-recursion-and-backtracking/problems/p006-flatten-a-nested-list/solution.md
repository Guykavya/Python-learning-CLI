## Approach

The structure is a tree: every list is a node, every plain value a leaf. Flattening is a left-to-right walk over the leaves. A list is flattened by flattening each of its items; a plain value is already flat. The base case is hidden in the loop: a list with no inner lists makes no recursive call.

## Code

```python
def flatten(xs):
    result = []
    for item in xs:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
```

## Complexity

Each `extend` copies the inner result once per level, so the time is `O(total items x depth)` in the worst case, at most `O(n * d)`. The depth of the recursion is the nesting depth `d`.

## Another way

Pass one shared output list down, so nothing is copied:

```python
def flatten(xs):
    out = []

    def go(items):
        for item in items:
            if isinstance(item, list):
                go(item)
            else:
                out.append(item)

    go(xs)
    return out
```

Or use a generator with `yield from flatten(item)` (chapter section 15).
