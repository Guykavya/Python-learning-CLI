## Hint 1

The sums: leaves `4 1 7 3 9 2 6 5`; level 2: `5, 10, 11, 11`; level 1: `15, 22`; root `37`. Node 5 is `[2,4)` with sum 10, node 6 is `[4,6)` with sum 11.

## Hint 2

`query(2, 6)`: the root is partial. Node 2 `[0,4)` is partial (it contains 0 and 1, outside the query). Its children: node 4 `[0,2)` is outside (`hi = 2 <= l = 2`), node 5 `[2,4)` is inside.

## Hint 3

`query(1, 7)` cuts into node 4 (`[0,2)` contains 0, which is outside) and into node 7 (`[6,8)` contains 7). Those two split down to leaves; nodes 5 and 6 are taken whole.
