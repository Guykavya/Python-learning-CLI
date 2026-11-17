## Hint 1

Inorder means the left subtree is **finished** before the node is visited. So from any node you first want to go left as far as you can, remembering the path. What data structure remembers a path and gives it back in reverse order?

## Hint 2

Use a variable `cur` for "where I am going down". While `cur` exists: push it, move to `cur.left`. When `cur` is `None`, pop a node from the stack: that node's left side is done, so visit it, and continue with its **right** child as the new `cur`.

## Hint 3

```
out, stack, cur = [], [], root
while cur is not None or stack:
    while cur is not None:       # go left as far as possible
        stack.append(cur)
        cur = cur.left
    cur = stack.pop()            # the next node in inorder
    out.append(cur.val)
    cur = cur.right              # then its right subtree
return out
```
