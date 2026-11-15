## Approach

Deduplication needs a **natural key** (here `id`: what makes two records "the same order") and a
**rule for which version wins** (here the latest `updated_at`, ties to the last seen).

Walk the records once and keep a dict `id -> (time, record)`. For each record parse its
timestamp into an aware `datetime`. Replace the stored entry when the new time is greater than
**or equal to** the stored one; `>=` is what makes a later duplicate win a tie.

Two details do the rest:

- Parsing matters. `"2024-06-01T09:00:00+05:30"` and `"2024-06-01T04:00:00Z"` compare the wrong
  way as strings. Aware datetimes compare by the real instant, whatever the offset.
- A dict keeps keys in first-insertion order and re-assigning a key does not move it, so the
  output is in first-seen order without any extra work.

## Code

```python
from datetime import datetime


def dedupe_latest(records: list[dict]) -> list[dict]:
    best: dict[int, tuple[datetime, dict]] = {}
    for record in records:
        when = datetime.fromisoformat(record["updated_at"])
        current = best.get(record["id"])
        if current is None or when >= current[0]:
            best[record["id"]] = (when, record)
    return [record for _, record in best.values()]
```

## Complexity

O(n) time for n records (one parse and one dict lookup each) and O(k) extra memory for k
distinct ids.

## Another way

Sort by `(time, position)` and let later items overwrite earlier ones in a dict, then restore
first-seen order:

```python
def dedupe_latest(records):
    first_pos = {}
    for i, r in enumerate(records):
        first_pos.setdefault(r["id"], i)
    winners = {}
    for i, r in sorted(enumerate(records), key=lambda p: (datetime.fromisoformat(p[1]["updated_at"]), p[0])):
        winners[r["id"]] = r            # the last one written is the latest (ties: latest position)
    return sorted(winners.values(), key=lambda r: first_pos[r["id"]])
```

This is O(n log n) and harder to read, but it is the same idea as the SQL version you would
write after an ELT load:
`ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC, loaded_seq DESC) = 1`.
