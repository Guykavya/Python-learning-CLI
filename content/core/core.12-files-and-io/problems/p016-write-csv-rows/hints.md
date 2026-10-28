## Hint 1

What does `csv.writer(f)` do with a field that contains a comma? And which `open()` argument must you pass so that the writer controls the line endings?

## Hint 2

```
with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(rows)
return len(rows)
```
