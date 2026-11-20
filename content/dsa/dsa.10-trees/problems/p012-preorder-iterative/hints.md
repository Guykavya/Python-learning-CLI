## Hint 1

What does the stack hold? The nodes that are still waiting to be visited. Start with just the root. In each step you take one node off the stack and visit it. What must you put on the stack so that its children are visited later, and in the right order?

## Hint 2

After visiting a node, push its children, but only those that exist. A stack is last in, first out, so to visit the **left** child first, push the **right** child first and the left child second.

## Hint 3

```
out = []
stack = [root] if root else []
while stack:
    node = stack.pop()
    out.append(node.val)
    if node.right: stack.append(node.right)
    if node.left:  stack.append(node.left)
return out
```
