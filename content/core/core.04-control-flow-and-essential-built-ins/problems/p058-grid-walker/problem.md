# Robot grid walker

A robot lives on a grid `W` columns wide and `H` rows tall. Columns are numbered `x = 0` to
`W - 1` (west to east) and rows `y = 0` to `H - 1` (south to north). It starts at `(0, 0)`
facing `north`.

The first line is `W H`. Then commands follow, one per line, until `stop`:

| Command | Effect |
|---|---|
| `move N` | step forward N times (N is a whole number of 1 or more) |
| `left`, `right` | turn 90 degrees |
| `turn around` | turn 180 degrees |
| `where` | print `At (x, y) facing <direction>` |
| blank line | ignored |
| anything else | print `Unknown: <line, stripped>` |

When a step would leave the grid, the robot stops moving for that command and prints
`Bumped into wall at (x, y)`, giving where it stopped. The rest of that `move` is cancelled.

After `stop`, print `Final: (x, y) facing <direction>` and `Steps: S`, where `S` counts the
steps actually taken.

**Example**

Input:
```
3 2
move 1
right
move 5
where
stop
```
Output:
```
Bumped into wall at (2, 1)
At (2, 1) facing east
Final: (2, 1) facing east
Steps: 3
```

Use `match` for the commands and for the facing direction.
