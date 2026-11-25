## Hint 1

Which question is answered first for a row: "have I seen this id?" or "is the number valid?" Why does the order matter when a duplicate row is also bad? And how will you notice a missing column before reading any row?

## Hint 2

```text
reader = csv.DictReader(handle); check reader.fieldnames contains column and each dedupe name (else KeyError(name))
report = four counters at 0; seen = set()
for row in reader:
    if dedupe_on: key = tuple(row[n] ...); if key in seen: report["duplicate"] += 1; continue; seen.add(key)
    parse cell -> missing / unparseable / value
    value out of [low, high] -> out_of_range
    else values.append(value)
```
