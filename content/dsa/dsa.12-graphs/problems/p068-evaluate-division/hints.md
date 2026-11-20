## Hint 1

Build a dictionary `adj` from each variable to a list of `(other, factor)`. From `a / b = k` you know `a = k * b`, so going from `a` to `b` multiplies by `k`; going from `b` to `a` multiplies by `1 / k`. Then a query `(x, y)` asks for a path from `x` to `y` and the product along it.

## Hint 2

Run a BFS (or DFS) from `x` that stores, for every vertex it reaches, the product from `x` to it: `product[v] = product[u] * factor`. A dictionary `product` doubles as the "seen" set. Stop when `y` is in it. Handle the unknown variables before the search.

## Hint 3

```
for (a, b), k in zip(equations, values): adj[a].append((b, k)); adj[b].append((a, 1 / k))
for x, y in queries:
    if x not in adj or y not in adj: answer -1.0; continue
    product = {x: 1.0};  queue = deque([x])
    while queue and y not in product:
        u = queue.popleft()
        for v, k in adj[u]: if v not in product: product[v] = product[u] * k; queue.append(v)
    answer product.get(y, -1.0)
```
