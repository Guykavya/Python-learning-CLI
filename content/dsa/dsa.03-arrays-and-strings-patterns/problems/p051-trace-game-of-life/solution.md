## Walkthrough: the blinker

Alive: row 2, columns 1 to 3.

| row | counts | why |
|---|---|---|
| 0 | `00000` | no alive cell in rows 0 and 1 |
| 1 | `12321` | each cell sees the part of row 2 below it: 1, 2, 3, 2, 1 alive cells |
| 2 | `11211` | the ends of the row see one alive neighbour; the middle sees two; columns 0 and 4 see one |
| 3 | `12321` | the same as row 1, from below |
| 4 | `00000` | |

Next grid: `(1, 2)` and `(3, 2)` are dead with 3, so they are born. `(2, 2)` is alive with 2 and stays. `(2, 1)` and
`(2, 3)` are alive with 1 and die. The row turns into a column.

## Walkthrough: the glider

Alive: `(0, 1)`, `(1, 2)`, `(2, 0)`, `(2, 1)`, `(2, 2)`.

| cell | alive now? | count | next |
|---|---|---|---|
| (0, 1) | yes | 1: only `(1, 2)` | dies |
| (1, 0) | no | 3: `(0, 1)`, `(2, 0)`, `(2, 1)` | born |
| (1, 1) | no | 5 | stays dead |
| (1, 2) | yes | 3: `(0, 1)`, `(2, 1)`, `(2, 2)` | stays |
| (2, 0) | yes | 1: only `(2, 1)` | dies |
| (2, 1) | yes | 3: `(1, 2)`, `(2, 0)`, `(2, 2)` | stays |
| (2, 2) | yes | 2: `(1, 2)`, `(2, 1)` | stays |
| (3, 1) | no | 3: the three cells of row 2 above it | born |

Every other cell is dead with a count other than 3 and stays dead. The top-left corner `(0, 0)` has only 3 cells
around it inside the grid, and one of them is alive: count 1.

## Output

```
counts
00000
12321
11211
12321
00000
next
.....
..#..
..#..
..#..
.....
counts
11210
35320
13220
23210
00000
next
.....
#.#..
.##..
.#...
.....
```

## Key ideas

- The count of a cell never includes the cell itself. That is why the blinker's middle has 2, not 3.
- The same count means different things for alive and dead cells: 2 keeps an alive cell, but does nothing for a dead one.
- Edges: cells outside the grid count as dead, so edge cells simply have fewer neighbours. If the glider grid wrapped
  around, row 4 would touch row 0 and column 4 would touch column 0. Then `(4, 0)`, `(4, 1)`, `(4, 2)` would see the
  alive `(0, 1)`, and `(1, 4)`, `(2, 4)`, `(3, 4)` would see the alive `(2, 0)`: their counts become 1 instead of 0. No
  count reaches 3, so the next grid would not change this time, but the digit rows would.
- Reading from `grid` and writing to `new` is what makes all cells change "at the same time".
