## Approach

The map changes only by adding land, and we need the number of islands after every change: exactly the "groups that keep merging" situation of chapter section 9. Each island is a group in a Union-Find.

A new land cell starts as its own island (`+1`). It then joins each neighbouring island; every **successful** union merges two different islands into one (`-1`). If the new cell touches the same island twice, the second union finds the same root, returns `False`, and the count does not drop again. A cell that is already land changes nothing.

Neighbours are found from `(r, c)` with bounds checks, not from the flat index: `i - 1` for the cell `(r, 0)` is the last cell of the previous row, which does not touch it.

```python
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
```

## Complexity

`O(rows * cols)` to set up the lists, then nearly `O(1)` per step (4 unions). With `k` steps: `O(rows * cols + k * alpha)`.

## Another way

Store `parent` in a dictionary that only gets keys for land cells, so a huge, mostly empty map costs nothing to set up. A flood fill (or recount) after each step is the brute force: `O(k * rows * cols)`.
