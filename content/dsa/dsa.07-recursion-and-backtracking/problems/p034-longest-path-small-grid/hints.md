## Hint 1

Fix a start cell. `go(r, c)` = the most moves possible from `(r, c)` when the cells on the current path are blocked. If no neighbour is free, it is 0.

## Hint 2

Mark `(r, c)`, compute `1 + go(neighbour)` for every free unvisited neighbour, keep the maximum, un-mark `(r, c)`, return the best. Do this for every start and keep the overall maximum.

## Hint 3

Pruning (optional): if the best found so far already equals `free cells - 1`, nothing can beat it, so you can stop.
