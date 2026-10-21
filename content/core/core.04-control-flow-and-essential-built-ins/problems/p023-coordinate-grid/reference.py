rows = int(input())
cols = int(input())
if rows == 0 or cols == 0:
    print("(empty grid)")
else:
    for r in range(1, rows + 1):
        line = ""
        for c in range(1, cols + 1):
            line += f"({r},{c}) "
        print(line.strip())
