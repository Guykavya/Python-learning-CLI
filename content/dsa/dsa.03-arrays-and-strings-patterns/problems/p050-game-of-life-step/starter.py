r, c, k = [int(x) for x in input().split()]
grid = [list(input().strip()) for _ in range(r)]

# TODO: repeat k times: build a NEW grid from the old one using the neighbour counts
for row in grid:
    print("".join(row))
