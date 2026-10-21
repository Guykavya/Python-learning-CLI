## Approach

Walk the top level. Plain items go straight into the result. A list item is the same problem,
smaller, so `flatten(item)` handles it, whatever its depth, and its items are added with
`extend`. A list with no list items is the hidden base case: the loop makes no recursive calls.

## Code

```python
def flatten(nested):
    """Return a new flat list of the non-list items in nested, in order."""
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result
```

## Complexity

O(total number of items and lists) time, if `extend` cost is counted per item; recursion depth equals the nesting depth.

## Another way

An explicit stack avoids the recursion limit for absurdly deep nesting: keep a list of iterators
and push one when you meet a sub-list. It is longer and harder to read; recursion matches the
shape of the data.
