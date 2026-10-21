## Approach

Cells are `(x, y)` tuples, which are hashable, so they can live in a set. Membership in a set is
O(1) on average, so 200,000 moves are quick.

## Code

```python
steps = {"U": (0, 1), "D": (0, -1), "L": (-1, 0), "R": (1, 0)}
x, y = 0, 0
visited = {(0, 0)}
revisits = 0
for move in input().strip():
    dx, dy = steps[move]
    x, y = x + dx, y + dy
    if (x, y) in visited:
        revisits += 1
    else:
        visited.add((x, y))
print("Visited:", len(visited))
print("Revisits:", revisits)
print(f"Final: ({x}, {y})")
```

## Complexity

O(n) for n moves. A list of visited cells would make each check O(n), so O(n²) overall.
