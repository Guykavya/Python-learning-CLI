# Trace BFS

This is the BFS of chapter section 3, with a `print` after each vertex leaves the queue and its neighbours have been handled. Predict **exactly** what it prints. Do not run it.

```python
from collections import deque

n = 7
edges = [(0, 2), (0, 1), (1, 3), (2, 4), (2, 3), (4, 5), (3, 5), (5, 6)]
adj = [[] for _ in range(n)]
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)

dist = {0: 0}
queue = deque([0])
while queue:
    u = queue.popleft()
    for v in adj[u]:
        if v not in dist:
            dist[v] = dist[u] + 1
            queue.append(v)
    print(f"pop {u}: queue={list(queue)} dist={dist}")
```

Write your answer in `answer.txt`, one printed line per line (seven lines). Each line shows the queue **after** `u` was taken out and its new neighbours were added (front of the queue first), and the dictionary `dist` as Python prints it: keys in the order they were **added**, not sorted.

## How to work

1. Build the adjacency lists on paper first, in edge-list order. For example, the edges `(0, 2)` and `(0, 1)` come first, so `adj[0] = [2, 1]`. Write all seven lists.
2. Keep three things: the queue, `dist` (in insertion order) and the vertex you are working on.
3. For each pop, go through `adj[u]` **in order**; a neighbour already in `dist` is skipped. A new one gets `dist[u] + 1` and goes to the **back** of the queue.

## After you answer

1. Vertex 3 can be reached as `0 -> 1 -> 3` and as `0 -> 2 -> 3`. Which vertex put it into the queue, and why does that not change `dist[3]`?
2. Why is `5` given distance 3 when `4` is popped, although `3` is also a neighbour of `5`?
3. Look at the `dist` values in the order they were added. Why are they never decreasing?
