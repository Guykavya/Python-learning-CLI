r, c = [int(x) for x in input().split()]
grid = [input().strip() for _ in range(r)]
row, col = [int(x) for x in input().split()]
commands = input().strip()

# TODO: directions in clockwise order N E S W with row/column changes; turn with % 4;
#       move only into free cells inside the grid; remember visited cells in a set
print(row, col, "N")
print(1)
