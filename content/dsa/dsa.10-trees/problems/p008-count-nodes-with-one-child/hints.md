## Hint 1

Finish the sentence: "`count_one_child(node)` returns the number of nodes with exactly one child in the tree that starts at `node`". At `node`, you know how many of its two children exist. What do you add for `node` itself, and what do you add from the two subtrees?

## Hint 2

Add `1` for the node if exactly one of `node.left`, `node.right` is `None`, otherwise add `0`. Then add the answers of both subtrees. The case "both children missing" and "both children present" must both add 0.

## Hint 3

```
if root is None: return 0
mine = 1 if (root.left is None) != (root.right is None) else 0
return mine + count_one_child(root.left) + count_one_child(root.right)
```
