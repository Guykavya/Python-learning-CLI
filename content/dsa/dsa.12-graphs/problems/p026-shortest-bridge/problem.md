# Shortest bridge

A grid is a list of strings of `'1'` (land) and `'0'` (water). Land cells that touch **up, down, left or right** form an island. The grid has **exactly two** islands.

Write `shortest_bridge(grid)`. It returns the smallest number of water cells you must turn into land so that the two islands become one (connected through up/down/left/right steps).

This combines two ideas of the chapter:

1. find all cells of **one** island (a flood fill, section 5);
2. grow outwards from **all** of those cells at once, one ring per step (multi-source BFS, section 3), until a ring touches the other island.

## Example

```python
>>> shortest_bridge(["010",
...                  "000",
...                  "001"])
2
>>> shortest_bridge(["11000",
...                  "10001",
...                  "00011"])
3
>>> shortest_bridge(["101"])
1
```

In the first grid the islands are the single cells at `(0, 1)` and `(2, 2)`. Turning `(1, 1)` and `(1, 2)` (or `(0, 2)` and `(1, 2)`) into land joins them: 2 cells.

## Constraints

- `1 <= rows, cols <= 300`. The grid is not changed (strings cannot be changed anyway).
- `O(rows * cols)` time. One test uses a 300 x 300 grid with two huge islands and runs your code with a **time limit**: comparing every cell of one island with every cell of the other is far too slow there.
- An island can be a long snake of 40,000 cells: a recursive flood fill hits the recursion limit, so use a stack or a queue.

## Think about

Why is a BFS that starts from a single cell of the first island wrong, even though BFS gives shortest paths? What is the distance of the first cell of the second island that the BFS reaches, and how does it relate to the number of flipped cells?
