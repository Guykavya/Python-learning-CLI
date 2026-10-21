# Game of Life

Conway's Game of Life is played on a grid of live (`#`) and dead (`.`) cells. In each
generation, every cell looks at its 8 neighbours (cells outside the grid count as dead):

- a live cell with 2 or 3 live neighbours stays alive; otherwise it dies;
- a dead cell with exactly 3 live neighbours becomes alive.

All cells change **at the same time**: the new generation is computed entirely from the old one.

Read `r c g`, then `r` lines of `c` characters. Print the grid after `g` generations.

**Example**

Input:
```
5 5 1
.....
..#..
..#..
..#..
.....
```
Output:
```
.....
.....
.###.
.....
.....
```

If you update the grid in place while you are still counting neighbours, later cells see
already-changed neighbours and the result is wrong.
