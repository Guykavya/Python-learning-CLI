## Hint 1

Each key of the report is a separate small question about the batch; compute them one at a
time. How do you read a column that may be missing from a row without a `KeyError`? What
goes wrong with `nulls / len(rows)` for an empty batch, and with `max(...)` when no row has a
timestamp? Which tool from `collections` counts how often each id appears?

## Hint 2

```
n = len(rows)
null_rate[col] = round(count(row.get(col) is None) / n, 3) if n else 0.0
counts = Counter(id for each row if id is not None)
duplicate_ids = sorted(id for id, c in counts.items() if c > 1)
out_of_range = [row id for row if amount is not None and not (low <= amount <= high)]
times = [updated_at that are not None]
newest = max(times) if times else None
fresh = newest is not None and now - newest <= max_age
```
