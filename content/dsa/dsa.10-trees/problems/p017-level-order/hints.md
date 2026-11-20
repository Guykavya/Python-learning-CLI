## Hint 1

A queue gives the nodes in the order they were found: first the root, then its children, then their children. All nodes of one level are in the queue **together** before the next level starts. How many of them are there, at the moment you start a level?

## Hint 2

At the start of each round, `len(queue)` is the number of nodes of the current level. Take exactly that many nodes from the front, put their values in one list, and append their children to the back. Those children are the next level.

## Hint 3

```
if root is None: return []
levels, queue = [], deque([root])
while queue:
    level = []
    for _ in range(len(queue)):
        node = queue.popleft()
        level.append(node.val)
        if node.left:  queue.append(node.left)
        if node.right: queue.append(node.right)
    levels.append(level)
return levels
```
