## Approach

An explicit stack replaces the recursion. Each vertex is pushed once; `depth` doubles as the "visited" array.

```python
import sys

data = sys.stdin.read().split()
n = int(data[0])
adj = [[] for _ in range(n + 1)]
for i in range(n - 1):
    u = int(data[1 + 2 * i])
    v = int(data[2 + 2 * i])
    adj[u].append(v)
    adj[v].append(u)

depth = [-1] * (n + 1)
depth[1] = 0
stack = [1]
while stack:
    u = stack.pop()
    for v in adj[u]:
        if depth[v] == -1:
            depth[v] = depth[u] + 1
            stack.append(v)
print(max(depth[1:]), sum(depth[1:]))
```

Example: for the edges `1-2, 2-3, 1-4, 4-5` the stack starts as `[1]`; popping 1 gives depths 2:1 and 4:1; popping 4 gives 5:2; popping 5, then 2 gives 3:2; the depths are `[0, 1, 2, 1, 2]` for vertices 1..5, so the answer is `2 6`.

The depth does not depend on the visiting order, so a stack (DFS order) and a queue (BFS order) give the same numbers.

## Complexity

`O(n)` time and memory. The worst case, a path with `n = 2 * 10**5`, uses a stack that never holds more than 2 vertices here and an adjacency list of `2 * 10**5` small lists.

## Another way

`threading.stack_size(...)` with a big stack and `sys.setrecursionlimit(10**6)` lets a recursive DFS survive (chapter section 8), but it is fragile (memory, platforms). The explicit stack is the habit to build.
