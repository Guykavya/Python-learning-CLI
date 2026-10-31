## Approach

Open the file with `newline=""` (the `csv` module wants to handle line endings itself, including line breaks inside quotes) and give it to `csv.DictReader`. Each row is a dict. Skip blank cells, convert the others with `float`, and add. A wrong column name raises `KeyError` by itself when you look it up.

## Code

```python
import csv


def sum_column(path, column):
    total = 0.0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cell = row[column]
            if cell.strip() != "":
                total += float(cell)
    return total
```

## Complexity

O(n) time, O(1) extra memory: the rows are read one at a time.

## Another way

Use `csv.reader` and find the column index from the header row. `DictReader` is easier to read, and it does not care about the order of the columns.
