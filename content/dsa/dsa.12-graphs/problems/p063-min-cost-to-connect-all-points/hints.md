## Hint 1

Prim needs, at every step, the cheapest edge from the tree to a point outside it. With a complete graph, you can keep one number per point: `best[v]` = the cheapest cost of joining `v` to **any** point already in the tree. How does `best` change when a new point `u` joins the tree?

## Hint 2

Start with `best = [inf] * n`, `best[0] = 0`. Repeat `n` times: pick the point `u` not in the tree with the smallest `best[u]` (a plain scan), add `best[u]` to the total, mark `u`, then for every point `v` outside the tree set `best[v] = min(best[v], dist(u, v))`.

## Hint 3

```
best = [inf] * n;  best[0] = 0;  in_tree = [False] * n;  total = 0
repeat n times:
    u = the index not in the tree with the smallest best[u]
    in_tree[u] = True;  total += best[u]
    for v not in the tree:
        best[v] = min(best[v], |xu - xv| + |yu - yv|)
return total
```
