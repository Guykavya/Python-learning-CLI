## Hint 1

Plain BFS works when every edge costs 1, because the queue holds distances in order. With 0-edges, a neighbour has the **same** distance as the vertex you are looking at. Where in the deque does a vertex with the current smallest distance belong?

## Hint 2

Keep `dist` with `inf` everywhere and `dist[source] = 0`; start with `deque([source])`. Pop from the left. For every edge `u -> v` with weight `w`: if `dist[u] + w < dist[v]`, set `dist[v]` and put `v` at the front when `w == 0`, at the back when `w == 1`. A vertex may enter the deque more than once; that is fine.

## Hint 3

```
dist = [inf] * n;  dist[source] = 0
dq = deque([source])
while dq:
    u = dq.popleft()
    for v, w in adj[u]:
        if dist[u] + w < dist[v]:
            dist[v] = dist[u] + w
            if w == 0: dq.appendleft(v)
            else:      dq.append(v)
return dist
```
