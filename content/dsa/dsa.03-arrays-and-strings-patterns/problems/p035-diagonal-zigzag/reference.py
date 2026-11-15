r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]

out = []
for d in range(r + c - 1):              # diagonal d holds the cells with i + j == d
    if d % 2 == 0:
        i = min(d, r - 1)               # even: start at the bottom-left end, walk up-right
        j = d - i
        while i >= 0 and j < c:
            out.append(grid[i][j])
            i -= 1
            j += 1
    else:
        j = min(d, c - 1)               # odd: start at the top-right end, walk down-left
        i = d - j
        while i < r and j >= 0:
            out.append(grid[i][j])
            i += 1
            j -= 1

print(" ".join(map(str, out)))
