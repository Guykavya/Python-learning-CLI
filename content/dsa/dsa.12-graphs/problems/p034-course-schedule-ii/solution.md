## Approach

The model is the same as in p033: a vertex per course and an edge `b -> a` for every pair `[a, b]`. A valid study plan is a topological order of that graph, and Kahn's algorithm (chapter section 7) builds one: it takes the courses whose prerequisites are all taken, in the order it frees them. If some courses are never freed, they sit on a cycle (or behind one), and no plan exists.

```python
from collections import deque


def find_order(num_courses, prerequisites):
    adj = [[] for _ in range(num_courses)]
    indeg = [0] * num_courses
    for a, b in prerequisites:
        adj[b].append(a)                           # b before a
        indeg[a] += 1
    ready = deque(c for c in range(num_courses) if indeg[c] == 0)
    order = []
    while ready:
        c = ready.popleft()
        order.append(c)
        for d in adj[c]:
            indeg[d] -= 1
            if indeg[d] == 0:
                ready.append(d)
    return order if len(order) == num_courses else []
```

## Complexity

`O(V + E)` time and memory.

## Another way

A DFS that records each course when it is finished and reverses the list (p032). With a DFS on the edges `a -> b` ("a needs b") you do not even need to reverse: a course finishes after all the courses it needs, so the finishing order itself is a valid plan. Both views are correct as long as you know which graph you built.
