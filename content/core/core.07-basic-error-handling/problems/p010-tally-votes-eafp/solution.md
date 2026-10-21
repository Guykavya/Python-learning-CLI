## Approach

`counts[name] += 1` reads `counts[name]` first, so for a new name it raises `KeyError` before
anything is stored. The handler stores the first vote. The `try` contains only that one line.

## Code

```python
def tally(votes):
    """Return a dict from cleaned candidate name to number of votes."""
    counts = {}
    for vote in votes:
        name = vote.strip().lower()
        if not name:
            continue
        try:
            counts[name] += 1
        except KeyError:
            counts[name] = 1
    return counts
```

## Complexity

O(n) for n votes (each dict operation is O(1) on average).

## Another way

`counts[name] = counts.get(name, 0) + 1` is the shortest and clearest version, and what you
should normally write. `collections.Counter` (a later module) does the whole job in one call.
The EAFP form is worth knowing because many situations have no `get`-like shortcut.
