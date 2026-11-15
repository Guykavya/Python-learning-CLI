r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]
# TODO: first find every row and column with an ORIGINAL zero, then write the zeros in a second pass
for row in grid:
    print(" ".join(map(str, row)))
