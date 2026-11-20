## Hint 1

Which course can be taken first? One that needs nothing. After it is taken, which courses may have become possible? This is p031 (Kahn) with one extra step: building the graph from `[a, b]` pairs.

## Hint 2

For each `[a, b]`: `adj[b].append(a)` and `indeg[a] += 1`. Run Kahn and collect the courses in the order you take them. If you took fewer than `num_courses`, return `[]`.

## Hint 3

```
for a, b in prerequisites: adj[b].append(a); indeg[a] += 1
ready = deque(c for c in range(num_courses) if indeg[c] == 0); order = []
while ready:
    c = ready.popleft(); order.append(c)
    for d in adj[c]:
        indeg[d] -= 1
        if indeg[d] == 0: ready.append(d)
return order if len(order) == num_courses else []
```
