## Approach

A course can be taken in semester `s` when all its prerequisites were taken in semesters before `s`. Taking it as early as possible is never worse, so the plan is: semester 1 takes every course with no prerequisites, semester 2 every course whose prerequisites are all in semester 1, and so on. That is Kahn's algorithm run in **rounds** (chapter section 7): the queue at the start of a round holds exactly the courses of that semester.

The number of rounds is the number of courses on the longest chain. Each course is taken one semester after the **latest** of its prerequisites, which is a longest-path rule (chapter section 7, "Dynamic programming on a DAG"), not a shortest-path rule. That is why a BFS distance (shortest number of steps from a start course) is wrong.

If there is a cycle, its courses never reach in-degree 0, so `done < n` and the answer is `-1`.

```python
from collections import deque


def min_semesters(n, relations):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in relations:
        adj[u].append(v)
        indeg[v] += 1
    ready = deque(v for v in range(n) if indeg[v] == 0)
    rounds = done = 0
    while ready:
        rounds += 1
        for _ in range(len(ready)):                # exactly the courses of this semester
            u = ready.popleft()
            done += 1
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    ready.append(v)
    return rounds if done == n else -1
```

## Complexity

Every course enters the queue once and every relation is used once: `O(n + E)`.

## Another way

Dynamic programming in topological order: `level[v] = 1 + max(level[u] for every edge u -> v)` (1 for courses without prerequisites); the answer is `max(level)`. It computes the same thing as the rounds. With a recursive memoised function `level(v)` it is short, but a chain of 100,000 courses passes the recursion limit.
