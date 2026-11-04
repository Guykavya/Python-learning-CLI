r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]
# TODO: for d = 0 .. r + c - 2, walk the cells with i + j == d; even d upward, odd d downward
out = []
for row in grid:
    out += row
print(" ".join(map(str, out)))
