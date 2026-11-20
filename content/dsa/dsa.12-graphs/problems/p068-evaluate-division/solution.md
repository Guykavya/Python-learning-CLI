## Approach

Model the equations as a weighted graph where an edge carries the factor between two variables. Any path from `x` to `y` gives the same product (the equations are consistent), so a BFS that multiplies along the way finds the answer. The `product` dictionary records which vertices have been reached, so cycles of equations cannot trap the search.

## Code

```python
from collections import defaultdict, deque


def evaluate(equations, values, queries):
    adj = defaultdict(list)
    for (a, b), k in zip(equations, values):
        adj[a].append((b, k))
        adj[b].append((a, 1 / k))
    answers = []
    for x, y in queries:
        if x not in adj or y not in adj:
            answers.append(-1.0)
            continue
        product = {x: 1.0}
        queue = deque([x])
        while queue and y not in product:
            u = queue.popleft()
            for v, k in adj[u]:
                if v not in product:
                    product[v] = product[u] * k
                    queue.append(v)
        answers.append(product.get(y, -1.0))
    return answers
```

Note `adj` is a `defaultdict`: the test `x not in adj` does not create an entry, but `adj[x]` would. Check with `in` first.

## Complexity

One BFS per query: `O(Q * (V + E))` time, `O(V + E)` memory.

## Another way

**Weighted Union-Find**: keep for every variable its root and the factor `value(variable) / value(root)`. Union two groups by setting one root's factor so that the new equation holds; a query `x / y` is `factor(x) / factor(y)` if they share a root. With path compression it answers each query in almost `O(1)`.
