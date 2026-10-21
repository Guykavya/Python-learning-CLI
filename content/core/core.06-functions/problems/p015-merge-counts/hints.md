## Hint 1

Where do the totals go: into the first input dict, or into a new dict?

## Hint 2

Counting with `get` (core.05): `totals[item] = totals.get(item, 0) + qty`.

## Hint 3

```
totals = {}
for one in counts:
    for item, qty in one.items():
        totals[item] = totals.get(item, 0) + qty
return {item: q for item, q in totals.items() if q != 0}
```
