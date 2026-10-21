r, c, g = [int(x) for x in input().split()]
grid = [list(input().strip()) for _ in range(r)]
for _ in range(g):
    new = [["."] * c for _ in range(r)]
    for i in range(r):
        for j in range(c):
            live = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if (di or dj) and 0 <= i + di < r and 0 <= j + dj < c:
                        if grid[i + di][j + dj] == "#":
                            live += 1
            if grid[i][j] == "#" and live in (2, 3):
                new[i][j] = "#"
            elif grid[i][j] == "." and live == 3:
                new[i][j] = "#"
    grid = new
for row in grid:
    print("".join(row))
