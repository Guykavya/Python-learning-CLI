## Approach

The outer loop produces rows, the inner loop produces the cells of one row. The inner loop
runs completely for every row.

## Code

```python
rows = int(input())
cols = int(input())
if rows == 0 or cols == 0:
    print("(empty grid)")
else:
    for r in range(1, rows + 1):
        line = ""
        for c in range(1, cols + 1):
            line += f"({r},{c}) "
        print(line.strip())
```

## Why reset `line` inside the outer loop

Each row starts empty. Created before the outer loop, `line` would keep growing, and row 2
would repeat row 1's cells.

## Another way

`print(f"({r},{c})", end=" ")` in the inner loop and `print()` after it. Each line then ends
with a space, which is usually invisible but can matter in exact comparisons.
