# Edit a copy, keep the original

Read `r` (the number of rows), then `r` lines of digits such as `0123` (rows may have different
lengths). Store the grid as a list of lists of single characters.

Make a **working copy** of the grid. Then read `k` and `k` edits `row col digit`, and apply
each edit to the **copy only**. Finally print:

```
Original:
<the original rows>
Edited:
<the edited rows>
Changed cells: <number of positions where the two grids differ>
```

An edit that writes the same digit that is already there does not count as a change.

**Example**

Input:
```
2
123
45
3
0 0 9
1 1 5
1 0 7
```
Output:
```
Original:
123
45
Edited:
923
75
Changed cells: 2
```

The edit `1 1 5` writes `5` where there already was a `5`, so it is not a change.
