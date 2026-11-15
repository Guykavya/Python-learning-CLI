# Maximal rectangle of 1s

A grid is given as a list of equal-length strings of `"0"` and `"1"`. Write two functions:

1. `histograms(grid)`: for every row, the list of **column heights**: how many `1`s stand in an unbroken column ending at this row. A `0` resets the height of its column to 0.
2. `maximal_rectangle(grid)`: the area of the largest rectangle that contains only `1`s.

The reduction (chapter section 10, "Maximal rectangle of 1s"): row by row, the heights form a histogram, and the largest rectangle whose **bottom edge** is on this row is the largest rectangle in that histogram (problem 34). The answer is the best over all rows.

## Example

```python
>>> grid = ["10100",
...         "10111",
...         "11111",
...         "10010"]
>>> histograms(grid)
[[1, 0, 1, 0, 0], [2, 0, 2, 1, 1], [3, 1, 3, 2, 2], [4, 0, 0, 3, 0]]
>>> maximal_rectangle(grid)
6
>>> maximal_rectangle([])
0
```

The best rectangle has its bottom on row 2: the heights there are `[3, 1, 3, 2, 2]`, and the last three columns give height 2 and width 3.

## Constraints

- `0 <= rows, cols <= 200`. An empty grid (`[]`) has area 0, and so does a grid of empty strings.

## Think about

Why is every all-1 rectangle found by this method? On which row is it found?
