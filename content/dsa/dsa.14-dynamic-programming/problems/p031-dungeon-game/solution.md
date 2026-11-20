## Approach

**Why not forwards?** The best path is not "the one with the most health at the end". In `[[0, -10, 20], [-2, -2, -2], [0, 0, 0]]` the path with the biggest total (8) dips to -10 and needs 11 at the start; the path through the -2s needs only 3. Forwards, a room would need two numbers (current health and lowest point so far) and neither one alone decides which path is better.

**Backwards it is one number.** What matters in room `(r, c)` is the future, and the future only asks: how much health must I have here?

- **State:** `need[r][c]` = the least health on entering `(r, c)` that is enough to reach the end alive.
- **Transition:** `need[r][c] = max(1, min(need[r+1][c], need[r][c+1]) - dungeon[r][c])`.
- **Base:** after the last room he just has to be alive (1). The `INF` border makes the "next room" outside the grid never win the `min`.
- **Answer:** `need[0][0]`.

The `max(1, ...)` is the key line: a big potion makes `after - dungeon[r][c]` small or negative, but he must still be alive when he walks in. A potion cannot be "saved up" from a future room to pay for a present one.

```python
INF = float("inf")


def min_initial_health(dungeon):
    rows, cols = len(dungeon), len(dungeon[0])
    # need[r][c] = least health on ENTERING (r, c) to survive to the end; INF border below and right
    need = [[INF] * (cols + 1) for _ in range(rows + 1)]
    need[rows][cols - 1] = need[rows - 1][cols] = 1      # "after" the last room you just need to be alive
    for r in range(rows - 1, -1, -1):
        for c in range(cols - 1, -1, -1):
            after = min(need[r + 1][c], need[r][c + 1])   # the cheaper next room
            need[r][c] = max(1, after - dungeon[r][c])
    return need[0][0]
```

Trace the classic example from the exit: `need[2][2] = max(1, 1 + 5) = 6`; `need[1][2] = max(1, 6 - 1) = 5`; `need[0][2] = max(1, 5 - 3) = 2`; `need[2][1] = max(1, 6 - 30) = 1`; `need[1][1] = max(1, min(1, 5) + 10) = 11`; `need[0][1] = max(1, min(11, 2) + 3) = 5`; `need[2][0] = max(1, 1 - 10) = 1`; `need[1][0] = max(1, min(1, 11) + 5) = 6`; `need[0][0] = max(1, min(6, 5) + 2) = 7`.

## Complexity

`O(rows * cols)` time and space (one row is enough for `O(cols)`).

## Another way

Binary search on the answer (dsa.05): for a fixed starting health `h`, a forward DP can keep "the most health left on entering each room", with dead states removed; that works because with `h` fixed only "alive or not" and "how much is left" matter. Find the smallest `h` that survives. It costs `O(rows * cols * log(max health))`; the tests use it as their checker on the big dungeon. The backward DP is faster and needs no search.
