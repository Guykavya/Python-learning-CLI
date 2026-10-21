## Approach

Read the matrix as a list of lists. Each row of the result is one column of the input, built
with an inner comprehension. The outer comprehension runs once per column.

## Code

```python
r, c = [int(x) for x in input().split()]
m = [[int(x) for x in input().split()] for _ in range(r)]
t = [[row[i] for row in m] for i in range(c)]
for row in t:
    print(" ".join(str(v) for v in row))
```

## Complexity

O(r × c): every number is visited once.

## Another way

`list(zip(*m))` transposes in one line: `*m` passes each row as a separate argument to `zip`,
which then pairs up the first items, the second items, and so on.
