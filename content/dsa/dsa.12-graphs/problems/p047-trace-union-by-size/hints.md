## Hint 1

The first two unions join two singletons each. Both roots have size 1, so no swap happens: the root of `y` goes under the root of `x`. `size` grows only at the new root, so after `union(0, 1)` it is `[2, 1, 1, 1, 1, 1, 1]`.

## Hint 2

`union(3, 1)`: the root of 3 is 2 and the root of 1 is 0. Both groups have size 2, so `rx = 2` stays (no strict "smaller"), and 0 goes under 2. Later, `find(1)` walks `1 -> 0 -> 2`; path compression then sets `parent[1] = 2` directly. Watch for the same thing with 5 in `union(6, 5)`.

## Hint 3

In `union(5, 1)` the root of 5 is 4 (size 2) and the root of 1 is 2 (size 4). 4's group is smaller, so the roots are swapped and 4 goes under 2. In the last call both elements already have root 2: `False`, and nothing changes.
