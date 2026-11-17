# Pacific Atlantic water flow

An island is a grid of heights (a list of lists of integers). The **Pacific** ocean touches the **top** and **left** edges of the island; the **Atlantic** touches the **bottom** and **right** edges. Rain on a cell flows to a neighbour (up, down, left, right) whose height is **less than or equal to** its own, and from there on in the same way. Water on a cell of the top row can flow into the Pacific directly, and so on for the other edges.

Write `pacific_atlantic(heights)`. It returns the **sorted** list of cells `(r, c)` (tuples) from which water can reach **both** oceans. An empty grid gives `[]`.

## Example

```python
>>> pacific_atlantic([[1, 2, 2, 3, 5],
...                   [3, 2, 3, 4, 4],
...                   [2, 4, 5, 3, 1],
...                   [6, 7, 1, 4, 5],
...                   [5, 1, 1, 2, 4]])
[(0, 4), (1, 3), (1, 4), (2, 2), (3, 0), (3, 1), (4, 0)]
```

From `(2, 2)` (height 5) water can go up and left down to the Pacific, and right and down to the Atlantic.

## Constraints

`0 <= rows, cols <= 300`, heights `0 .. 10**5`. A search from **every** cell costs `O((rows * cols)^2)`, which is far too slow for 300 x 300; the tests run such a grid in a separate process with a 10-second limit. Aim for `O(rows * cols)`.
