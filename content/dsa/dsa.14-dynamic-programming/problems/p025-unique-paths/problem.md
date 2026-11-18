# Unique paths

A robot stands on the top-left cell of a grid with `rows` rows and `cols` columns. It may only move **right** or **down**, one cell at a time. Write `unique_paths(rows, cols)` that returns the number of different paths to the bottom-right cell.

## Example

```python
>>> unique_paths(3, 7)
28
>>> unique_paths(3, 2)        # right-down-down, down-right-down, down-down-right
3
>>> unique_paths(1, 1)        # start = end: one path (stand still)
1
>>> unique_paths(1, 5)        # one row: only "right, right, right, right"
1
```

## Constraints

- `1 <= rows, cols <= 1000`. The answer can be a very big integer; Python handles it.
- A top-down recursion would be up to 2,000 calls deep for a 1000 by 1000 grid, past Python's limit (section 3). Fill a table: a full one, or one rolling row (section 6).

## Think about

1. Through which two cells must every path to `(r, c)` pass just before it arrives?
2. What are the values on the whole first row and the whole first column? Why?
3. Section 6 does this with **one** list. When you update `row[c] = row[c] + row[c - 1]`, which cell does each of the two terms stand for?
