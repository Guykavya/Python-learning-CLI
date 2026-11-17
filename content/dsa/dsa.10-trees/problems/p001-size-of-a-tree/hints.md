## Hint 1

Do not think about the whole tree. Finish the sentence "`size(node)` returns the number of nodes in the tree that starts at `node`". If someone already gave you `size(node.left)` and `size(node.right)`, what is missing to get the answer for `node`?

## Hint 2

The missing piece is the node itself: 1. The empty tree is the base case: nothing there means 0 nodes. Two cases only.

## Hint 3

```
if root is None: return 0
return 1 + size(root.left) + size(root.right)
```
