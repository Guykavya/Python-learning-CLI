## Hint 1

What should you do with `None` and `""` *before* counting, so that they land in one bucket? Which tool counts items?

## Hint 2

```text
labels = [("(missing)" if v is None or v == "" else v) for v in values]
counts = Counter(labels)
total = len(labels)
rows = [(v, c, round(100 * c / total, 1)) for v, c in counts.items()]
rows.sort(key=lambda r: (-r[1], r[0]))
```
