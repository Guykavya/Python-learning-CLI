## Approach

Iterating a dict gives names. The key turns each name into `(-score, name)`. The smallest such
tuple belongs to the highest score, and among equal scores to the alphabetically first name, so
`min` gives the answer. `default=None` covers the empty dict (core.04).

## Code

```python
def top_scorer(scores):
    """Return the name with the highest score (alphabetically first on a tie), or None if empty."""
    return min(scores, key=lambda name: (-scores[name], name), default=None)
```

## Complexity

O(n).

## Another way

Find the best score first, then the smallest name with that score:
```python
if not scores:
    return None
best = max(scores.values())
return min(name for name in scores if scores[name] == best)
```
Two passes, but each is very easy to read.
