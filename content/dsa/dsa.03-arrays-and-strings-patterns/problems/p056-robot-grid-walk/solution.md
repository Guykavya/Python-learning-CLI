## Approach

A plain simulation, made short and safe by three habits:

1. **Direction arrays.** Directions in clockwise order `N E S W`, with `dr = [-1, 0, 1, 0]` and `dc = [0, 1, 0, -1]`.
   Turning right adds 1 to the index, turning left subtracts 1, both modulo 4 (`+ 3` is the same as `- 1` modulo 4 and
   never negative).
2. **Check before you read.** Bounds first, then the wall. In Python, `grid[-1]` is the last row, so a missing `0 <=`
   check makes the robot wrap around the grid without any error.
3. **A set for visited cells.** Revisiting a cell must not count twice, and a set answers "seen before?" in O(1).

## Code

```python
r, c = [int(x) for x in input().split()]
grid = [input().strip() for _ in range(r)]
row, col = [int(x) - 1 for x in input().split()]
commands = input().strip()

NAMES = "NESW"
DR = [-1, 0, 1, 0]
DC = [0, 1, 0, -1]
d = 0

visited = {(row, col)}
for ch in commands:
    if ch == "L":
        d = (d + 3) % 4
    elif ch == "R":
        d = (d + 1) % 4
    elif ch == "F":
        nr, nc = row + DR[d], col + DC[d]
        if 0 <= nr < r and 0 <= nc < c and grid[nr][nc] != "#":
            row, col = nr, nc
            visited.add((row, col))

print(row + 1, col + 1, NAMES[d])
print(len(visited))
```

## Hand check: the example

| commands | position after | facing | new cells |
|---|---|---|---|
| start | (5, 2) | N | 1 |
| F | (4, 2) | N | 2 |
| F | blocked by (3, 2) | N | 2 |
| L F | (4, 1) | W | 3 |
| R F F | (2, 1) | N | 5 |
| R F F F F | (2, 5) | E | 9 |
| R F F F | (5, 5) | S | 12 |
| F | blocked (row 6 does not exist) | S | 12 |

## Complexity

O(r * c) to read the grid, then O(1) per command: O(r * c + m) for `m` commands. The set holds at most `r * c` cells.

## Another way

Use complex numbers: position `row + col * 1j`, step `-1` for North. A right turn multiplies the step by `-1j`, a left
turn by `1j`. It is compact but harder to read; the direction arrays generalise directly to 8 directions (add the
diagonals in clockwise order and turn by 2 for 90 degrees).
