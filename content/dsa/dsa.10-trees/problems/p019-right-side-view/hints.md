## Hint 1

What do you see at depth `d`? The node that comes **last** when you list depth `d` from left to right. So if you can get all the levels from left to right, what is the answer?

## Hint 2

Do a level-order walk. For each level, keep the value of the last node (the one read at the end of the inner loop), or the last element of the finished level list.

## Hint 3

```
if root is None: return []
view, queue = [], deque([root])
while queue:
    size = len(queue)
    for i in range(size):
        node = queue.popleft()
        if i == size - 1:
            view.append(node.val)
        append the left child, then the right child
return view
```
