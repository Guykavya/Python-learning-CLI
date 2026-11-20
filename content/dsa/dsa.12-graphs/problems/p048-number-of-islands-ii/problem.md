# Number of islands II (online)

A map of `rows x cols` cells starts as all water. `positions` is a list of cells `(r, c)`; they are turned into land **one at a time**, in that order. Land cells that touch **up, down, left or right** form an island.

Write `islands_after_each(rows, cols, positions)`. Return a list with the number of islands **after each** step.

Running a flood fill after every step (chapter section 5) costs `O(rows * cols)` per step, far too slow for 100,000 steps. Union-Find (chapter section 9) answers it **online**: when a cell becomes land it is a new island (`count += 1`); then for each of its land neighbours, if they are in different groups, unite them and do `count -= 1`.

Rules:

- A cell can appear in `positions` more than once. Turning land into land changes nothing: report the same count again.
- Number the cell `(r, c)` as `r * cols + c` if you want a flat index, but check the neighbours with `0 <= r < rows` and `0 <= c < cols`: cell `(1, 0)` and cell `(0, cols - 1)` are neighbours in the flat numbering, but **not** on the map.

## Example

```python
>>> islands_after_each(3, 3, [(0, 0), (0, 1), (1, 2), (2, 1), (1, 1)])
[1, 1, 2, 3, 1]
>>> islands_after_each(1, 2, [(0, 0), (0, 0), (0, 1)])
[1, 1, 1]
>>> islands_after_each(2, 2, [(0, 1), (1, 0)])        # diagonal cells are separate islands
[1, 2]
```

In the first example the last step, `(1, 1)`, touches three separate islands (`{(0,0),(0,1)}`, `{(1,2)}` and `{(2,1)}`) and joins them into one: `3 + 1 - 3 = 1`.

## Constraints

- `1 <= rows, cols <= 1000`, `1 <= len(positions) <= 10**5`. One test runs 100,000 steps on a `300 x 300` map with a time limit. Nearly `O(1)` per step.

## Think about

When a new land cell touches the **same** island from two sides (say from the left and from above), how many times must the count go down? How does Union-Find tell you?
