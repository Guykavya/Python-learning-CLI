r, c = [int(x) for x in input().split()]
grid = [[int(x) for x in input().split()] for _ in range(r)]

best = grid[0][0]
# TODO: for every top row, start column sums at 0; for every bottom row >= top, add that row to the
# column sums and run Kadane on them.
print(best)
