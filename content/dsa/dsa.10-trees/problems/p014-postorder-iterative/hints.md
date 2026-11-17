## Hint 1

Write the postorder as `L, R, node`. Now read it backwards: `node, R, L`. That is a preorder where the **right** child is visited before the left one. So: visit nodes in the order node, right, left, and reverse the result at the end.

## Hint 2

In the iterative preorder you pushed the right child first so that the left child came out first. For "node, right, left" you want the right child on top of the stack, so push the **left** child first and the right child second. Collect the values in a list and reverse it at the end.

## Hint 3

```
out = []
stack = [root] if root else []
while stack:
    node = stack.pop()
    out.append(node.val)          # node, then right, then left ...
    if node.left:  stack.append(node.left)
    if node.right: stack.append(node.right)
return out[::-1]                  # ... reversed: left, right, node
```
(The one-stack way: go left and push; look at the top; if it has an unvisited right child go there, otherwise visit it and remember it in `last`.)
