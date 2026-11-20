def islands_after_each(rows, cols, positions):
    parent = list(range(rows * cols))
    size = [1] * (rows * cols)
    land = [False] * (rows * cols)

    def find(x):
        root = x
        while parent[root] != root:
            root = parent[root]
        while parent[x] != root:
            parent[x], x = root, parent[x]
        return root

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        if size[ra] < size[rb]:
            ra, rb = rb, ra
        parent[rb] = ra
        size[ra] += size[rb]
        return True

    count, out = 0, []
    for r, c in positions:
        i = r * cols + c
        if not land[i]:
            land[i] = True
            count += 1                             # a new island of one cell
            for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                if 0 <= nr < rows and 0 <= nc < cols and land[nr * cols + nc]:
                    if union(i, nr * cols + nc):
                        count -= 1                 # two islands became one
        out.append(count)
    return out
