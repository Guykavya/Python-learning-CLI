## Hint 1

A schedule is impossible exactly when some courses wait for each other in a circle. Which property of a directed graph is that? Which algorithm from section 7 notices it without recursion?

## Hint 2

Build the graph with an edge `b -> a` for every `[a, b]` and count in-degrees. Kahn: start with all courses of in-degree 0, take them one by one, lower the in-degree of the courses that need them. Count how many courses you took.

## Hint 3

```
adj = [[] for _ in range(num_courses)]; indeg = [0] * num_courses
for a, b in prerequisites: adj[b].append(a); indeg[a] += 1
ready = deque(c for c in range(num_courses) if indeg[c] == 0); taken = 0
while ready:
    c = ready.popleft(); taken += 1
    for d in adj[c]:
        indeg[d] -= 1
        if indeg[d] == 0: ready.append(d)
return taken == num_courses
```
