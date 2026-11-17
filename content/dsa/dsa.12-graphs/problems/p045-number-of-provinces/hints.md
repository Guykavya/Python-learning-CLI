## Hint 1

When you start a search at a city nobody has visited yet, you have found a new province. Which cities does that search visit? What must you do so that the same province is not counted again?

## Hint 2

Union-Find version: `groups = n`. For every pair `i < j` with `is_connected[i][j] == 1`, unite `i` and `j`; each successful union lowers `groups` by one. Search version: a `seen` list; for each unseen city, count one province and visit everything reachable (the neighbours of `u` are the `j` in row `u` with a 1).

## Hint 3

```
n = len(is_connected); seen = [False] * n; provinces = 0
for s in range(n):
    if seen[s]: continue
    provinces += 1; seen[s] = True; stack = [s]
    while stack:
        u = stack.pop()
        for v in range(n):
            if is_connected[u][v] == 1 and not seen[v]:
                seen[v] = True; stack.append(v)
return provinces
```
