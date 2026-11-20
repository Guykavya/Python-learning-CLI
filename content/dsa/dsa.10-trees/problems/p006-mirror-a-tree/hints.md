## Hint 1

Finish the sentence: "`invert(node)` returns the root of the mirror image of the tree that starts at `node`". If the two subtrees are already inverted by the recursive calls, what is left to do at `node` itself?

## Hint 2

Swap the two children. The danger is the order of the assignments: after `node.left = something`, the old left child is gone. A tuple assignment computes the right side first:

`node.left, node.right = invert(node.right), invert(node.left)`

## Hint 3

```
if root is None: return None
root.left, root.right = invert(root.right), invert(root.left)
return root
```
