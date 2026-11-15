# Robot walk on a grid with walls

A robot stands on a grid of free cells `.` and walls `#`. It starts on a given free cell, **facing North** (towards
row 1). It then follows a string of commands, one character at a time:

| command | meaning |
|---|---|
| `L` | turn left 90 degrees (N -> W -> S -> E -> N) |
| `R` | turn right 90 degrees (N -> E -> S -> W -> N) |
| `F` | move one cell forward, **unless** that cell is a wall or outside the grid: then the command is skipped and the robot stays where it is (still facing the same way) |

Print where the robot ends, which way it faces, and how many **different** cells it has stood on (the start cell
counts).

Rows are numbered from 1 at the top, columns from 1 at the left. North is "row - 1", East is "column + 1", South is
"row + 1", West is "column - 1".

## Input

- Line 1: `r c`.
- Then `r` lines of `c` characters (`.` or `#`).
- Next line: the start `row col` (1-based, always a free cell).
- Last line: the commands (only `L`, `R`, `F`). It can be **empty**: then the robot does nothing.

## Output

- Line 1: `row col dir`, where `dir` is one of `N`, `E`, `S`, `W`.
- Line 2: the number of different cells visited.

## Example

Input:

```
5 5
..#..
.....
.##..
.....
#....
5 2
FFLFRFFRFFFFRFFFF
```

Output:

```
5 5 S
12
```

Step by step: from (5, 2) facing N, `F` goes to (4, 2); the next `F` is blocked by the wall at (3, 2). `L` faces W, `F`
to (4, 1). `R` faces N, `F F` to (3, 1) and (2, 1). `R` faces E, four `F` to (2, 2), (2, 3), (2, 4), (2, 5). `R` faces S,
`F F F` to (3, 5), (4, 5), (5, 5); the last `F` would leave the grid and is skipped. The visited cells are (5, 2),
(4, 2), (4, 1), (3, 1), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (3, 5), (4, 5), (5, 5): 12.

## Constraints

- `1 <= r, c` and `r * c <= 250000`
- At most 200000 commands.

Use `input()` without a prompt message.

## Plan before you code

Use **direction arrays**: put the directions in clockwise order `N E S W` with `dr = [-1, 0, 1, 0]` and
`dc = [0, 1, 0, -1]`. Then a right turn is `d = (d + 1) % 4` and a left turn is `d = (d + 3) % 4`: no `if` chain of
sixteen cases. Store the visited cells in a **set** of `(row, col)` pairs.
