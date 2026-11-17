## Hint 1

Keep a dictionary `copy_of` from **old node** to **new node** (node objects can be dictionary keys: they are compared by identity). What should happen when you meet a node that is already in the dictionary? What should happen the first time you meet it?

## Hint 2

Do a BFS over the old graph. When a node is seen for the first time, make its copy (with an empty `neighbors` list), store it in `copy_of`, and put the old node in the queue. When you take an old node `u` out of the queue, walk through `u.neighbors` **in order** and append `copy_of[v]` to `copy_of[u].neighbors`.

## Hint 3

```
if node is None: return None
copy_of = {node: Node(node.val)}
queue = deque([node])
while queue:
    u = queue.popleft()
    for v in u.neighbors:
        if v not in copy_of:
            copy_of[v] = Node(v.val)
            queue.append(v)
        copy_of[u].neighbors.append(copy_of[v])
return copy_of[node]
```
