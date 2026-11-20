def unique_paths(rows, cols):
    row = [1] * cols                     # first row: one way to each cell
    for r in range(1, rows):
        for c in range(1, cols):
            row[c] = row[c] + row[c - 1]  # above (old row[c]) + left (new row[c-1])
    return row[cols - 1]
