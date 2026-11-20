## Hint 1

The weights are 4, 2, 4, 3, 2, 2, 5, 1. Sorted: the 1 first, then the three edges of weight 2 in their original order `(1, 2)`, `(3, 4)`, `(4, 5)`, then the 3, the two 4s in order, and the 5.

## Hint 2

After taking `3-5` the parents are `[0, 1, 2, 5, 4, 5]`. After `1-2`: `parent[1] = 2`. After `3-4`: the root of 3 is 5, so `parent[5] = 4`. Now `find(5)` gives 4 and `find(4)` gives 4: what happens to `4-5`?
