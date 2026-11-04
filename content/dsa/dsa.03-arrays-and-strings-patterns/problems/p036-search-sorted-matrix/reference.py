r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]
q = int(input())
targets = [int(x) for x in input().split()]

out = []
for x in targets:
    i, j = 0, c - 1                  # top-right corner
    found = False
    while i < r and j >= 0:
        v = grid[i][j]
        if v == x:
            found = True
            break
        if v > x:
            j -= 1                   # everything below in this column is even bigger: drop the column
        else:
            i += 1                   # everything left in this row is even smaller: drop the row
    out.append("yes" if found else "no")
print("\n".join(out))
