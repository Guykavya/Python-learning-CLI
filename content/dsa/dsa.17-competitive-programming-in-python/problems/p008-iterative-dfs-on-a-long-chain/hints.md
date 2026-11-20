## Hint 1

You need the depth of every vertex, not the order of a real DFS. What data structure replaces the call stack of a recursion? Which vertices go on it?

## Hint 2

Build an adjacency list: `adj[u]` holds the neighbours of `u`. Keep `depth = [-1] * (n + 1)` where `-1` means "not visited yet" (it also stops you from walking back to the parent).

## Hint 3

```text
depth[1] = 0
stack = [1]
while stack:
    u = stack.pop()
    for v in adj[u]:
        if depth[v] == -1:
            depth[v] = depth[u] + 1
            stack.append(v)
answer: max(depth[1:]) and sum(depth[1:])
```
