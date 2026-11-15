# Longest path in a small grid

`grid` is a list of equal-length strings with `"."` for free cells and `"#"` for walls. A path starts at **any** free cell, moves up, down, left or right through free cells, and never visits a cell twice. Write `longest_path(grid)` that returns the largest number of **moves** (steps) of such a path.

A grid with one free cell has answer 0 (no move is possible). A grid with no free cell also has answer 0.

## Example

```python
>>> longest_path(["...", "...", "..."])
8
>>> longest_path([".#.", "...", ".#."])
4
>>> longest_path(["#"])
0
```

In the 3x3 open grid a snake through all 9 cells has 8 moves. In the plus-shaped second grid no path can visit all 7 cells; the best has 5 cells, so 4 moves.

## Constraints

- `1 <= rows, cols <= 4` (at most 16 cells).

## Think about

This is a **maximum** over all paths, not a count. Each call can return "the most moves I can still make from here", and the parent takes the best child plus one. What is the answer from a cell whose neighbours are all used?
