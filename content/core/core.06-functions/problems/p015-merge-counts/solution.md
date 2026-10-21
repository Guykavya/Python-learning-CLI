## Approach

`*counts` gives a tuple of the caller's dicts, which are the caller's real objects. So build the
totals in a brand new dict, and only ever **read** the inputs. Filtering zeros at the end with a
comprehension builds yet another new dict instead of deleting during a loop.

## Code

```python
def merge_counts(*counts):
    """Return a new dict of total quantities per item across all dicts, dropping zero totals."""
    totals = {}
    for one in counts:
        for item, qty in one.items():
            totals[item] = totals.get(item, 0) + qty
    return {item: q for item, q in totals.items() if q != 0}
```

## Complexity

O(total number of entries across all dicts).

## Another way

`collections.Counter` can add counts, but it drops non-positive totals with `+`, which would also
drop legitimate negative totals here. The explicit loop says exactly what we want.
