r, c = [int(x) for x in input().split()]
grid = [input().strip() for _ in range(r)]
row, col = [int(x) - 1 for x in input().split()]     # 0-based inside the program
commands = input().strip()

NAMES = "NESW"                         # clockwise order: R = +1, L = -1 (that is, +3)
DR = [-1, 0, 1, 0]                     # row change for N, E, S, W
DC = [0, 1, 0, -1]                     # column change
d = 0                                  # facing North

visited = {(row, col)}
for ch in commands:
    if ch == "L":
        d = (d + 3) % 4
    elif ch == "R":
        d = (d + 1) % 4
    elif ch == "F":
        nr, nc = row + DR[d], col + DC[d]
        if 0 <= nr < r and 0 <= nc < c and grid[nr][nc] != "#":
            row, col = nr, nc
            visited.add((row, col))

print(row + 1, col + 1, NAMES[d])
print(len(visited))
