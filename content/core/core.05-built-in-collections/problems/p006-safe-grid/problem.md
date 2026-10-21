# A grid with independent rows

Read `rows cols` on the first line, then a number `k`, then `k` lines of `r c` positions.
Start with a grid of `.` characters, mark each position with `#`, and print the grid, one row
per line with no spaces.

**Example**

Input:
```
3 4
2
0 0
2 3
```
Output:
```
#...
....
...#
```

Marking one cell must change **only** that cell. If marking `0 0` puts a `#` at the start
of every row, your rows are secretly the same list.
