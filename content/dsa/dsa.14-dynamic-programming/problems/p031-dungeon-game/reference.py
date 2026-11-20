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
