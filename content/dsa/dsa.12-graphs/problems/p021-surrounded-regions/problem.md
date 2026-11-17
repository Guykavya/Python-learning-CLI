# Surrounded regions

A board is a list of strings of `"X"` and `"O"`. A region of `"O"` cells (joined up, down, left, right) is **captured** when it is completely surrounded by `"X"`: none of its cells is on the border of the board. Captured regions turn into `"X"`. Regions that touch the border survive.

Write `capture(board)`. It returns a **new** list of strings with every captured region turned into `"X"`. The caller's list must not change. An empty board `[]` gives `[]`.

## Example

```python
>>> capture(["XXXX",
...          "XOOX",
...          "XXOX",
...          "XOXX"])
['XXXX', 'XXXX', 'XXXX', 'XOXX']
```

The region `(1,1) (1,2) (2,2)` is surrounded and is captured. The `"O"` at `(3,1)` is on the bottom border: it survives.

## Constraints

`0 <= rows, cols <= 300`. `O(rows * cols)` time. The tests include a 300 x 300 board of `"O"` (nothing is captured there); a recursive search would go 90,000 calls deep.
