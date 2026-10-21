## Approach

The "missing go last in both directions" rule is easiest if the missing records never enter the
sort at all. Partition the list, sort only the records that have the field, and append the
others. `reverse=True` keeps the sort stable, so equal values keep their order in both
directions.

## Code

```python
def sort_records(records, field, *, descending=False):
    """Return records sorted by record[field]; records without the field go last, in order."""
    have = [r for r in records if field in r]
    missing = [r for r in records if field not in r]
    return sorted(have, key=lambda r: r[field], reverse=descending) + missing
```

## Complexity

O(n log n).

## Another way

A single sort with a tuple key that puts missing records last, such as
`key=lambda r: (field not in r, r.get(field, 0))`, works only for ascending order and only if the
placeholder `0` can be compared with the real values. The partition is simpler and safer.
