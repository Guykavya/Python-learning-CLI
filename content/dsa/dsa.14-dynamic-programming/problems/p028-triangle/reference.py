def min_triangle_path(triangle):
    below = list(triangle[-1])                  # g on the bottom row: just the values
    for i in range(len(triangle) - 2, -1, -1):  # rows from the second-last up to the top
        row = triangle[i]
        below = [row[j] + min(below[j], below[j + 1]) for j in range(len(row))]
    return below[0]
