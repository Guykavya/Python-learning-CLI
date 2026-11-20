## Hint 1

The lists are `adj[0] = [1, 4]`, `adj[1] = [0, 2, 3]`, `adj[2] = [1, 3]`, `adj[3] = [1, 2]`, `adj[4] = [0, 5]`, `adj[5] = [4]`. `visit(0)` enters `0` at time 0 and then calls `visit(1)` at once, because `1` is the first neighbour.

## Hint 2

From `1`: `0` is visited, so the next neighbour `2` is entered; from `2` the first unvisited neighbour is `3`. In `3` both neighbours are visited, so `3` exits right away. Then the calls return one by one. When the loop of `1` reaches `3`, it is already visited. Only after `1` exits does `0` try its second neighbour `4`.
