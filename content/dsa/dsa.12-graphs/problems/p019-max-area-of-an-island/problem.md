# Max area of an island

Same map as in p018: a list of strings, `"1"` is land, `"0"` is water, and land cells joined **up, down, left or right** form one island. The **area** of an island is its number of cells.

Write `max_area(grid)`. It returns the area of the largest island, or `0` if there is no land (also for `[]`). Do not change the caller's list.

## Example

```python
>>> max_area(["11000",
...           "11010",
...           "00011",
...           "10000"])
4
>>> max_area(["000"])
0
```

The islands have areas 4, 3 and 1.

## Constraints

`0 <= rows, cols <= 300`. `O(rows * cols)` time. The tests include an all-land 300 x 300 map (area 90,000), so a recursive search crashes; use an explicit stack or a queue.
