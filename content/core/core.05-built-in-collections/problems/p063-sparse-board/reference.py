cells = {}
row_sum = {}
col_sum = {}
while True:
    parts = input().split()
    match parts:
        case ["end"]:
            break
        case ["set", r, c, v]:
            r, c, v = int(r), int(c), int(v)
            old = cells.get((r, c), 0)
            row_sum[r] = row_sum.get(r, 0) - old + v
            col_sum[c] = col_sum.get(c, 0) - old + v
            if v == 0:
                cells.pop((r, c), None)
            else:
                cells[(r, c)] = v
        case ["get", r, c]:
            print(cells.get((int(r), int(c)), 0))
        case ["row", r]:
            print(row_sum.get(int(r), 0))
        case ["col", c]:
            print(col_sum.get(int(c), 0))
        case ["count"]:
            print(len(cells))
