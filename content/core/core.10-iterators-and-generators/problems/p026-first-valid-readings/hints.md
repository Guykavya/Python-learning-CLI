## Hint 1

You have many iterables but want to treat them as one. Which itertools tool joins
iterables end to end, without copying them?

## Hint 2

Build it as three lazy stages: join the sources, keep only valid readings, take the first `n`.
Only the last step (`list(...)`) actually pulls values.

## Hint 3

```
readings = chain(*sources)
valid = (r for r in readings if r is not None and 0 <= r <= 50)
return list(islice(valid, n))
```
