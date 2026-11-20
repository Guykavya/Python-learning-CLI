# Trace Bellman-Ford rounds

This is the Bellman-Ford of chapter section 12 on a small directed graph with negative edges, with a print after every round. Predict **exactly** what it prints. Do not run it.

```python
INF = float("inf")


def bellman_ford_traced(n, edges, source):
    dist = [INF] * n
    dist[source] = 0
    for rnd in range(1, n):
        changed = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                changed = True
        shown = ["-" if x == INF else x for x in dist]
        print(f"round {rnd}: {shown}")
        if not changed:
            print("no change: stop")
            break
    return dist


edges = [(3, 4, 2), (2, 3, -1), (1, 2, 3), (0, 1, 4), (0, 2, 9), (1, 3, 5), (0, 4, 1), (4, 1, -2)]
print(bellman_ford_traced(6, edges, 0))
```


Write your answer in `answer.txt`, one printed line per line (six lines). An infinite distance is shown as `'-'` inside the round lines (with quotes, as Python prints a string inside a list); the returned list on the last line shows `inf`.

## How to work

The **order of the edges matters** inside a round: a distance lowered by an early edge is used at once by a later edge in the **same** round. So go through the eight edges one by one, in the listed order, and keep the list `dist` on paper. An edge only counts when its start `dist[u]` is not infinite and `dist[u] + w` is **strictly** smaller than `dist[v]`. After each round, write the line; if nothing changed in that round, the program also prints `no change: stop` and ends.

Vertex 5 has no edges at all.

## After you answer

1. After round 1, which distances are already final, and which are still too large?
2. The best route to vertex 3 has how many edges? Why did it need until round 3 to appear?
3. The loop allows up to `n - 1 = 5` rounds. How many ran, and why is stopping after a round without changes safe?
