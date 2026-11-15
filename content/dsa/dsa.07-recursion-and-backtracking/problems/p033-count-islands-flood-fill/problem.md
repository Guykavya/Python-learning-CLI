# Count islands with flood fill

`grid` is a list of equal-length strings: `"#"` is land and `"."` is water. An **island** is a group of land cells connected up, down, left or right (diagonal neighbours do **not** connect). Write `count_islands(grid)` that returns the number of islands. Do not change `grid`.

## Example

```python
>>> count_islands(["##..",
...                "#...",
...                "..##",
...                "...#"])
2
>>> count_islands(["#.#",
...                ".#."])
3
```

## Constraints

- `1 <= rows, cols <= 60`.
- One test has a single snake-shaped island of more than 1,200 cells.

## Think about

Start with the recursive flood fill: when you meet unvisited land, count one island and visit everything connected to it. That passes every test except the snake: a recursive fill there goes more than 1,000 calls deep and raises `RecursionError`. Then turn the fill into a loop with an **explicit stack** (chapter section 15). Do not raise the recursion limit.
