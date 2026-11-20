# Trace Dijkstra

This is the lazy Dijkstra of chapter section 10 on a small **undirected** weighted graph, with a print after every pop. Predict **exactly** what it prints. Do not run it.

```python
import heapq

INF = float("inf")


def dijkstra_traced(n, edges, source):
    adj = [[] for _ in range(n)]
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    dist = [INF] * n
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            print(f"pop ({d}, {u}): stale, skip")
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (d + w, v))
        shown = ["-" if x == INF else x for x in dist]
        print(f"pop ({d}, {u}): heap {sorted(heap)}  dist {shown}")
    return dist


edges = [(0, 1, 7), (0, 2, 2), (2, 1, 3), (1, 3, 1), (2, 3, 8), (3, 4, 2), (2, 4, 9)]
print(dijkstra_traced(5, edges, 0))
```


Write your answer in `answer.txt`, one printed line per line (nine lines). Copy the format exactly:

- a normal pop prints the heap **after** all the pushes of that pop, as a **sorted** list of `(distance, vertex)` pairs, then two spaces, then `dist`, where an infinite distance is shown as the string `'-'` (Python prints it with quotes inside a list);
- a stale pop prints only `pop (d, u): stale, skip`;
- the last line is the returned list.

## How to work

1. Build the adjacency list first, in the order of the edge list: every edge `(u, v, w)` adds `(v, w)` to `adj[u]` **and** `(u, w)` to `adj[v]`. Write the five lists down.
2. Keep two things on paper: the heap as a set of pairs, and the list `dist`.
3. For each pop: take the smallest pair. If its distance is bigger than `dist[u]`, it is stale. Otherwise relax the neighbours of `u` in list order: push only when `d + w < dist[v]` (strictly smaller). The old pair of a vertex whose distance dropped **stays** in the heap.

## After you answer

1. Which vertex had its distance lowered twice, and through which vertices?
2. How many pairs were pushed in total, and how many of them turned out stale? Why can the heap hold more pairs than there are vertices?
3. The edge `2 - 4` (weight 9) was used once. Is it part of any shortest route in the end?
