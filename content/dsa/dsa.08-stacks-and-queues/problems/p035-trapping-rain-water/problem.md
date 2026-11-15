# Trapping rain water

Bars of width 1 stand side by side with heights `height`. After rain, water collects between them. Write `trap(height)` that returns the total amount of trapped water (in unit squares).

Water above bar `i` reaches the level `min(highest bar on its left, highest bar on its right)`; if that level is above the bar, the difference is water. Water at the edges runs away.

Use a **decreasing stack** of indices (chapter section 10, "Trapping rain water"): when a higher bar arrives, the top of the stack is the bottom of a pool, the bar below it is the left wall, and the new bar is the right wall. Each pop adds one horizontal layer of water. A two-pointer solution is also accepted.

## Example

```python
>>> trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])
6
>>> trap([4, 2, 0, 3, 2, 5])
9
>>> trap([3, 0, 3])
3
>>> trap([1, 2, 3])
0
```

## How it is tested

Known examples, flat and V shapes, 1,000 random lists compared with the per-bar formula, and 100,000 bars.

## Constraints

- `0 <= len(height) <= 10**5`, `0 <= height[i] <= 10**4`.

## Think about

Why does a pool need a left wall? What should happen when you pop the bottom of a pool and the stack is then empty?
