# Game of Life generations

Conway's Game of Life is a grid of cells, each **alive** (`#`) or **dead** (`.`). Every cell has up to 8 neighbours
(including the diagonal ones). All cells change **at the same time**, by these rules:

- an alive cell with **2 or 3** alive neighbours stays alive; otherwise it dies;
- a dead cell with **exactly 3** alive neighbours becomes alive; otherwise it stays dead.

Cells outside the grid are **dead**: the grid does **not** wrap around. A cell on the edge simply has fewer
neighbours (a corner has 3).

Print the grid after `k` generations.

The trap: "at the same time". If you change a cell and then count its neighbour using the changed value, the
result is wrong. Every count must use the grid as it was at the start of the generation.

## Input

- Line 1: `r c k`.
- Then `r` lines of `c` characters, each `#` or `.`.

## Output

`r` lines: the grid after `k` generations.

## Example

Input:

```
5 5 1
.....
.....
.###.
.....
.....
```

Output:

```
.....
..#..
..#..
..#..
.....
```

The middle cell of the row has 2 alive neighbours and stays. The two ends have only 1 and die. The cells just above
and below the middle see all three alive cells and are born. After 2 generations the row is back: this pattern is
called a *blinker*.

## Constraints

- `1 <= r, c <= 100`
- `0 <= k <= 10` (with `k = 0` print the grid unchanged)

Use `input()` without a prompt message.
