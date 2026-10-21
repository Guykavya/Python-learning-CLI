## Approach

Build a list of lists, then flatten with a two-`for` comprehension. Read it as nested loops:
for each row, for each value in that row.

## Code

```python
n = int(input())
rows = [[int(x) for x in input().split()] for _ in range(n)]
flat = [v for row in rows for v in row]
print(" ".join(str(v) for v in flat) if flat else "(empty)")
print("Total:", sum(flat))
best = None
for i, row in enumerate(rows):
    if best is None or len(row) > len(rows[best]):
        best = i
print("Longest row:", "none" if best is None else best)
```

## Complexity

O(total numbers).

## Reading order

`[v for row in rows for v in row]` equals:

```python
flat = []
for row in rows:
    for v in row:
        flat.append(v)
```
