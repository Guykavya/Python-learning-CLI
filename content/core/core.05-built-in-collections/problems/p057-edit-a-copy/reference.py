r = int(input())
grid = [list(input().strip()) for _ in range(r)]
work = [row[:] for row in grid]
k = int(input())
for _ in range(k):
    i, j, digit = input().split()
    work[int(i)][int(j)] = digit
print("Original:")
for row in grid:
    print("".join(row))
print("Edited:")
for row in work:
    print("".join(row))
changed = sum(1 for i in range(r) for j in range(len(grid[i])) if grid[i][j] != work[i][j])
print("Changed cells:", changed)
