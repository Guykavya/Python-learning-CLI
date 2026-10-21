## Approach

Negating the marks turns "high first" into "small first", so a single ascending sort with the key
`(-marks, name.lower())` handles both orders at once. Then pull out the names and slice when
`top` was given.

## Code

```python
def rank_students(records, *, top=None):
    """Return names ordered by marks (high first), ties by name ignoring case; only `top` if given."""
    ranked = sorted(records, key=lambda r: (-r[1], r[0].lower()))
    names = [name for name, marks in ranked]
    if top is None:
        return names
    return names[:top]
```

## Complexity

O(n log n).

## Another way

Two stable sorts: first `sorted(records, key=lambda r: r[0].lower())`, then sort that by marks with
`reverse=True`. Python's sort keeps equal items in order even with `reverse=True`, so the names
stay A-to-Z within each mark.
