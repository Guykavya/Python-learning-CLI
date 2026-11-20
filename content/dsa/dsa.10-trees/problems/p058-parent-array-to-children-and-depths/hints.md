## Hint 1

First build `children`: for every node `i` whose `parent[i]` is not `-1`, append `i` to `children[parent[i]]`. If you go through `i` from `0` upwards, the children of each node come out in increasing order. Where is the root?

## Hint 2

Now the depths. If the parent can have a larger number than its child, `depth[parent[i]]` may not be known yet when you reach `i`. Start from the root (`depth 0`) and visit the nodes breadth-first: take a node from the queue, and for each of its children set `depth[child] = depth[node] + 1` and put the child in the queue. Every node is reached after its parent.

## Hint 3

```
n = len(parent)
children = [[] for _ in range(n)]
for node, p in enumerate(parent):
    if p == -1: root = node
    else:       children[p].append(node)
depth = [0] * n
queue = deque([root])
while queue:
    node = queue.popleft()
    for c in children[node]:
        depth[c] = depth[node] + 1
        queue.append(c)
return children, depth
```
