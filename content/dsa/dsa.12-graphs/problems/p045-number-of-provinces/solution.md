## Approach

Provinces are the connected components of the road graph. Count them as in chapter section 5: go through the cities; each one that is not yet visited starts a new component, and a search from it visits the whole component. The matrix gives the neighbours of `u` as the columns `v` with a `1` in row `u`, so looking at one city costs `n` steps.

```python
def count_provinces(is_connected):
    n = len(is_connected)
    seen = [False] * n
    provinces = 0
    for s in range(n):
        if seen[s]:
            continue
        provinces += 1                             # a new province starts here
        seen[s] = True
        stack = [s]
        while stack:
            u = stack.pop()
            for v in range(n):
                if is_connected[u][v] == 1 and not seen[v]:
                    seen[v] = True
                    stack.append(v)
    return provinces
```

## Complexity

Every city is popped once and its row is scanned once: `O(n^2)`, which is the size of the input anyway.

## Another way

Union-Find (chapter section 9): start with `n` groups and for every `i < j` with a road, `union(i, j)`; every union that merges two groups lowers the count by one. With a matrix this is also `O(n^2)` (plus almost nothing per union). It is the better tool when roads arrive one by one and you need the count after each road.
