# Why Dijkstra fails with negative edges

Dijkstra's algorithm settles the vertex with the smallest tentative distance and never improves it again. Chapter section 10 proves this is safe when all weights are non-negative, and shows a graph with a negative edge where the textbook version (with a `done` set) gives a wrong answer.

Write a short explanation (10 to 15 sentences) in `answer.md` that does the following:

1. **Give your own counterexample** with exactly **3 vertices** `0, 1, 2`, source `0`, directed edges, one of them negative, and **no negative cycle**. Give the edge list, the true shortest distances, and the distances that the `done`-set Dijkstra below returns. They must differ.
2. Point to the exact sentence of the proof that breaks: which step assumed that "the rest of the route can only add"?
3. Explain why **adding a constant** to every weight (to make them all non-negative) does not fix it. Use a route with 1 edge and a route with 2 edges between the same two vertices.
4. Which algorithm of this chapter does handle negative edges, and what does it do instead of "settle the closest"? What does it cost?
5. The chapter's **lazy** version (`if d > dist[u]: continue`) got the chapter's example right. Is it then safe with negative edges? Say what can happen to its running time.

You may test your counterexample with this code (it is the chapter's `done`-set Dijkstra and Bellman-Ford, for a list of edges):

```python
import heapq

def dijkstra_done_set(n, edges, source):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
    dist = [float("inf")] * n
    dist[source] = 0
    done = set()
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in done:
            continue
        done.add(u)
        for v, w in adj[u]:
            if v not in done and d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
    return dist

def bellman_ford(n, edges, source):
    dist = [float("inf")] * n
    dist[source] = 0
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist

edges = []          # your counterexample, for example [(0, 1, ...), ...]
print(dijkstra_done_set(3, edges, 0), bellman_ford(3, edges, 0))
```

Then compare with the model answer and rate yourself.
