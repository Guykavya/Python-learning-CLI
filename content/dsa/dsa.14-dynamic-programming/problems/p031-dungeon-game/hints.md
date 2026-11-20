## Hint 1

Going forwards you would need two numbers per path (the health now **and** the lowest point so far), and the best path for one is not the best for the other. Going backwards there is one number per room. Define `need[r][c]` = the smallest health the knight must have when he **enters** room `(r, c)` (before its effect) to reach the end alive. What is `need` for the last room?

## Hint 2

Last room: after its effect he must have at least 1, so `need = max(1, 1 - dungeon[r][c])`. Any other room: after its effect he must have at least the need of the cheaper next room, `after = min(need below, need right)`. So `need[r][c] = max(1, after - dungeon[r][c])`. Why the `max(1, ...)`? Fill from the bottom-right corner, row by row upwards, right to left.

## Hint 3

An `INF` border on the bottom and the right removes the edge cases; seed the two border cells next to the exit with 1:

```
need = (rows+1) x (cols+1) of INF
need[rows][cols-1] = need[rows-1][cols] = 1
for r from rows-1 down to 0:
    for c from cols-1 down to 0:
        need[r][c] = max(1, min(need[r+1][c], need[r][c+1]) - dungeon[r][c])
return need[0][0]
```
