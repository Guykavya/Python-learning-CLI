## Approach

Open with `"w"`, `newline=""` and UTF-8. Create a `csv.writer`, write the header with `writerow`, then the rows with `writerows`. The writer adds quotes only where needed and doubles inner quotes. The writer ends lines with `\r\n`; `newline=""` stops Python from changing that again, which would make `\r\r\n` on Windows.

## Code

```python
import csv


def write_rows(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    return len(rows)
```

## Complexity

O(total size).

## Another way

Use `csv.DictWriter` when your rows are dicts. Then you give `fieldnames` and call `writeheader()`.
