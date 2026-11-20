## Approach

Model first. Courses are vertices; a prerequisite `[a, b]` is an edge `b -> a` ("`b` before `a`"). All courses can be taken exactly when the graph has a topological order, that is, when it has no directed cycle (chapter section 7).

Kahn's algorithm takes courses whose remaining prerequisites are all done. If a cycle exists, its courses never become free, so fewer than `num_courses` are taken.

```python
from collections import deque


def can_finish(num_courses, prerequisites):
    adj = [[] for _ in range(num_courses)]
    indeg = [0] * num_courses
    for a, b in prerequisites:
        adj[b].append(a)                           # b must come before a
        indeg[a] += 1
    ready = deque(c for c in range(num_courses) if indeg[c] == 0)
    taken = 0
    while ready:
        c = ready.popleft()
        taken += 1
        for d in adj[c]:
            indeg[d] -= 1
            if indeg[d] == 0:
                ready.append(d)
    return taken == num_courses
```

## Complexity

`O(V + E)` time and memory, with `V = num_courses` and `E = len(prerequisites)`.

## Another way

DFS with three colours (chapter section 6, p030): there is no schedule exactly when the DFS finds an edge to a GREY vertex. For this yes/no question the direction of the edges does not even matter: reversing every edge keeps every cycle a cycle. It matters in p034, where you must return the order.
