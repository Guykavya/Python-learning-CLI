## The printed lines

```text
union(0, 1) -> True: parent=[0, 0, 2, 3, 4, 5, 6] size=[2, 1, 1, 1, 1, 1, 1]
union(2, 3) -> True: parent=[0, 0, 2, 2, 4, 5, 6] size=[2, 1, 2, 1, 1, 1, 1]
union(3, 1) -> True: parent=[2, 0, 2, 2, 4, 5, 6] size=[2, 1, 4, 1, 1, 1, 1]
union(4, 5) -> True: parent=[2, 0, 2, 2, 4, 4, 6] size=[2, 1, 4, 1, 2, 1, 1]
union(5, 1) -> True: parent=[2, 2, 2, 2, 2, 4, 6] size=[2, 1, 6, 1, 2, 1, 1]
union(6, 5) -> True: parent=[2, 2, 2, 2, 2, 2, 2] size=[2, 1, 7, 1, 2, 1, 1]
union(0, 6) -> False: parent=[2, 2, 2, 2, 2, 2, 2] size=[2, 1, 7, 1, 2, 1, 1]
```

## Walkthrough

1. `union(0, 1)`: roots 0 and 1, sizes 1 and 1, no swap. `parent[1] = 0`, `size[0] = 2`.
2. `union(2, 3)`: the same: `parent[3] = 2`, `size[2] = 2`.
3. `union(3, 1)`: `find(3)` is 2 (one step), `find(1)` is 0 (one step, nothing to compress). Sizes 2 and 2: no swap, so `rx = 2`. `parent[0] = 2`, `size[2] = 4`. The tree is now `2 -> {0, 3}`, `0 -> {1}`.
4. `union(4, 5)`: `parent[5] = 4`, `size[4] = 2`.
5. `union(5, 1)`: `find(5)` is 4. `find(1)` walks `1 -> 0 -> 2`, root 2; compression sets `parent[1] = 2` (0 already points at 2). Sizes: 4's group has 2, 2's group has 4, so they swap: `rx = 2`, `ry = 4`. `parent[4] = 2`, `size[2] = 6`. Now 5 still points at 4.
6. `union(6, 5)`: `find(6)` is 6. `find(5)` walks `5 -> 4 -> 2`; compression sets `parent[5] = 2`. Sizes 1 and 6: swap, `parent[6] = 2`, `size[2] = 7`.
7. `union(0, 6)`: both roots are 2. `False`, no change.

## Answers to "After you answer"

1. Only `size[2] = 7` is meaningful: 2 is the only root. The values at 0 (2) and 4 (2) are left over from when those elements were roots of groups of two; the 1s at the other positions are left over from the start. The code only reads `size` of roots, so the stale values never matter.
2. `union(5, 1)` changed `parent[1]` from 0 to 2, and `union(6, 5)` changed `parent[5]` from 4 to 2. Neither 1 nor 5 was one of the two roots being joined.
3. Without compression the final `parent` would be `[2, 0, 2, 2, 2, 4, 2]`: 1 hangs under 0 and 5 under 4, so the tree has height 2. Union by size alone keeps the height at most `log2(7)`, about 2.8; compression flattens it further as `find` walks the paths.

## Complexity

Each operation costs the length of the path that `find` walks; with both tricks this is amortised nearly constant (p049).

## Another way to check your answer

After every line, draw the forest from `parent` and check two things: every element's root is the same as before for elements that were not merged, and the `size` of every **root** equals the number of elements in its tree.
