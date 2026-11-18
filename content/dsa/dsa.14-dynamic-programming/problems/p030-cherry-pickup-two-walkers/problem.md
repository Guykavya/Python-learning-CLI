# Cherry pickup (two walkers)

`grid` is an `n` by `n` square. Each cell is `1` (a cherry), `0` (empty) or `-1` (a thorn bush you cannot enter). You walk from the top-left cell to the bottom-right cell moving only **right or down**, and then walk back to the top-left moving only **left or up**. Each cherry you pass is picked, and a picked cell becomes empty: a cell visited twice gives its cherry only once. Write `cherry_pickup(grid)` that returns the most cherries you can pick. If there is no way to the bottom-right cell (or the start or end is a thorn), return 0.

## Example

```python
>>> cherry_pickup([[0, 1, -1],
...                [1, 0, -1],
...                [1, 1,  1]])
5
>>> cherry_pickup([[1, 1, 0],
...                [1, 1, 1],
...                [1, 0, 1]])
7
>>> cherry_pickup([[1, 1, -1],
...                [1, -1, 1],
...                [-1, 1, 1]])     # thorns cut every route
0
```

First example: down, down, right, right picks 4; the way back (left, up, up, left) passes `(1, 1)` and `(0, 1)` and picks the last one: 5 in total.

## Constraints

- `1 <= n <= 50`.
- The obvious plan, "take the best single trip, remove its cherries, then take the best second trip", **is wrong** (see the second example). Both trips must be planned together.
- This idea is not in the chapter. The hints teach it.

## Think about

1. The way back is a right/down path read backwards. So the problem is: **two** walkers go from the top-left to the bottom-right at the same time. What do they pick?
2. If both walkers have made `t` steps, walker 1 is at `(r1, t - r1)` and walker 2 at `(r2, t - r2)`. How many numbers describe the whole situation? That is your state.
3. When do the two walkers stand on the same cell, and how do you avoid counting that cherry twice?
