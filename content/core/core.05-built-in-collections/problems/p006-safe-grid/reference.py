rows, cols = [int(x) for x in input().split()]
grid = [["."] * cols for _ in range(rows)]
k = int(input())
for _ in range(k):
    r, c = [int(x) for x in input().split()]
    grid[r][c] = "#"
for row in grid:
    print("".join(row))
