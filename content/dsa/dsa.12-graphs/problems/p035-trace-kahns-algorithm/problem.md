# Trace Kahn's algorithm

This is Kahn's algorithm from chapter section 7, with a `print` after every step. Predict **exactly** what the program prints. Do not run it.

```python
from collections import deque


def kahn_traced(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        adj[u].append(v)
        indeg[v] += 1
    ready = deque(v for v in range(n) if indeg[v] == 0)
    print(f"start: ready={list(ready)} indeg={indeg}")
    order = []
    while ready:
        u = ready.popleft()
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                ready.append(v)
        print(f"take {u}: ready={list(ready)} indeg={indeg}")
    print("order:", order if len(order) == n else "cycle")


kahn_traced(6, [(3, 1), (4, 1), (4, 0), (1, 2), (0, 2), (2, 5), (0, 5)])
kahn_traced(4, [(0, 1), (1, 2), (2, 1), (2, 3)])
```

Write your answer in `answer.txt`, one printed line per line (11 lines). Lists are printed the way Python prints them, for example `ready=[3, 4]`. The `take` line shows `ready` and `indeg` **after** the taken vertex's edges were removed.

## How to work

For the first graph, write the adjacency lists first, in the order the edges are listed (for example `adj[4] = [1, 0]`). Then count the in-degrees: how many edges end at each vertex. The starting queue holds the vertices with in-degree 0, in increasing order (that is how the `deque(...)` line builds it).

Then do the loop on paper. Take the **leftmost** vertex of `ready`. Walk through its adjacency list **in order**: lower each target by one, and if it reaches 0, add it to the **right** end of `ready`. Only then write the line.

The second graph has a cycle. Stop the loop when `ready` is empty and decide which last line is printed.

## After you answer

1. In the first graph, vertex 1 reaches in-degree 0 before vertex 0 does, although `adj[4] = [1, 0]` lowers both in the same step. Why does 1 come out first?
2. In the second graph, which vertices are never taken, and what are their in-degrees at the end? Why can neither of them ever reach 0?
3. Vertex 3 in the second graph is not on the cycle. Why is it never taken either?
