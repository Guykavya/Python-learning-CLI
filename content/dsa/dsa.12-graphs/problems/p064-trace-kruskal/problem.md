# Trace Kruskal

This is Kruskal's algorithm of chapter section 15 with a very simple Union-Find (no union by size, no path compression) and a print for every edge it looks at. Predict **exactly** what it prints. Do not run it.

```python
def kruskal_traced(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            x = parent[x]
        return x

    order = sorted(edges, key=lambda e: e[2])     # by weight; equal weights keep their order
    print("sorted:", order)
    total, taken = 0, 0
    for u, v, w in order:
        ru, rv = find(u), find(v)
        if ru == rv:
            print(f"skip {u}-{v} ({w}): same group")
            continue
        parent[ru] = rv
        total += w
        taken += 1
        print(f"take {u}-{v} ({w}): total {total}")
        if taken == n - 1:
            print("tree complete")
            break
    return total


edges = [(0, 1, 4), (1, 2, 2), (0, 2, 4), (2, 3, 3), (3, 4, 2), (4, 5, 2), (1, 3, 5), (3, 5, 1)]
print(kruskal_traced(6, edges))
```


Write your answer in `answer.txt`, one printed line per line (nine lines). The first line shows the whole sorted list as Python prints it.

## How to work

1. Sort the edges by weight. `sorted` is **stable**: edges with the same weight stay in the order they had in the list.
2. Keep the `parent` list on paper (start `[0, 1, 2, 3, 4, 5]`). `find(x)` follows parents until a vertex is its own parent. A union sets `parent[root of u] = root of v` (the root of `u` goes under the root of `v`).
3. For every edge, find both roots: same root means `skip`, different roots means `take`. Stop after `n - 1 = 5` taken edges; edges after that are never looked at.

## After you answer

1. Write the `parent` list after the last union. Which vertex is the root of the whole tree?
2. Which edges were never looked at, and why does that not change the answer?
3. If the edge `(4, 5, 2)` had been listed before `(3, 4, 2)`, which of the two would have been skipped? Would the total change?
