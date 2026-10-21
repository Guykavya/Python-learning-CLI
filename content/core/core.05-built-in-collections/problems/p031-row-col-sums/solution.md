## Approach

A list of lists. Rows are easy to sum. Each column sum walks down every row at one index.

## Code

```python
r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]
for row in grid:
    print(" ".join(str(v) for v in row), "=", sum(row))
cols = [sum(row[j] for row in grid) for j in range(c)]
print("Columns:", " ".join(str(v) for v in cols))
print("Total:", sum(cols))
```

## Complexity

O(r × c): each number is added twice, once for its row and once for its column.
