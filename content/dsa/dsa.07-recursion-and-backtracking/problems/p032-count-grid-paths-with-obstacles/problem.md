# Number of paths in a grid with obstacles

`grid` is a list of equal-length strings; `"."` is a free cell and `"#"` is a wall. Write `count_paths(grid)` that returns the number of different paths from the **top-left** cell to the **bottom-right** cell that move up, down, left or right through free cells and **never visit a cell twice**.

If the start or the end cell is a wall, the answer is 0. A 1x1 free grid has one path (you are already there).

## Example

```python
>>> count_paths(["...", "...", "..."])
12
>>> count_paths(["..", ".."])
2
>>> count_paths([".#", ".."])
1
```

## Constraints

- `1 <= rows, cols <= 5`, and at most 16 free cells in the tests with more than 4 rows and columns.

## Think about

Unlike "only right and down" moves, paths here can wander back up. There is no formula: you must walk all of them (chapter section 10, "Counting paths in a grid"). Why do you need to un-mark a cell when the search leaves it?
