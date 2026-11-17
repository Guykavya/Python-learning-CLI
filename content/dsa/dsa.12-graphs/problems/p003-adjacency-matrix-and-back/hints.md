## Hint 1

`[[0] * n] * n` looks like a table, but it is one row repeated `n` times. Set `m[0][1] = 1` and print `m`: what happened to the other rows? Build each row separately.

## Hint 2

```
to_matrix:  m = [[0] * n for _ in range(n)]
            for u, v in edges: m[u][v] = 1; if not directed: m[v][u] = 1
to_edges:   for u in range(n):
                start = 0 if directed else u        # undirected: only v >= u
                for v in range(start, n):
                    if matrix[u][v]: out.append((u, v))
```
