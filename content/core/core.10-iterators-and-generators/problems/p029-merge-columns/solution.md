## Approach

`zip_longest(*columns, fillvalue=fill)` walks all columns side by side. When a column runs out,
it gives `fill` in its place, and it stops when the **longest** column ends. `*columns` passes
each column as a separate argument. For each row, turn the values into strings and join them.

## Code

```python
from itertools import zip_longest


def csv_lines(columns, fill=""):
    for row in zip_longest(*columns, fillvalue=fill):
        yield ",".join(str(value) for value in row)
```

## Complexity

O(rows * columns) time. The generator holds one row at a time.

## Another way

Without `zip_longest`: find the longest length, then for each index read `column[i]` if it
exists, otherwise `fill`. That needs lists (with `len` and indexing), so it does not work when
a column is a generator. `zip_longest` works on any iterables.
