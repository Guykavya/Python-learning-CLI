# Number of islands

A map is a list of strings: `"1"` is land and `"0"` is water. Land cells that touch **up, down, left or right** belong to the same island; touching only at a corner (diagonally) does not join them. Every island is a connected component of the grid graph (chapter section 5, "Islands on a grid").

Write `num_islands(grid)`. It returns the number of islands. An empty list `[]` has no islands.

Do not change the caller's list. (Strings cannot be changed anyway; if you want to "sink" visited land, work on a copy.)

## Example

```python
>>> num_islands(["11000",
...              "11010",
...              "00011",
...              "10000"])
3
>>> num_islands(["101",
...              "010",
...              "101"])
5
```

In the second map the five land cells touch only at corners: five islands.

## Constraints

`0 <= rows, cols <= 300`. `O(rows * cols)` time. The tests include a map that is **all land** (100 x 100 and 300 x 300): a recursive search goes 10,000 calls deep there and crashes, so use an explicit stack or a queue.
