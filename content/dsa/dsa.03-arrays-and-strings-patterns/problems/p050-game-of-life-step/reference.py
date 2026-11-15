r, c, k = [int(x) for x in input().split()]
grid = [list(input().strip()) for _ in range(r)]

for _ in range(k):
    new = [["."] * c for _ in range(r)]
    for i in range(r):
        for j in range(c):
            alive = 0
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = i + di, j + dj
                    if 0 <= ni < r and 0 <= nj < c and grid[ni][nj] == "#":
                        alive += 1
            if grid[i][j] == "#":
                new[i][j] = "#" if alive in (2, 3) else "."
            else:
                new[i][j] = "#" if alive == 3 else "."
    grid = new

for row in grid:
    print("".join(row))
