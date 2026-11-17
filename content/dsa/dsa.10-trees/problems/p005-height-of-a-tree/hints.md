## Hint 1

Finish the sentence: "`height(node)` returns the number of nodes on the longest downward path from `node`". What is the height of the empty tree under the "count nodes" convention? A path can go left or right: which of the two do you want?

## Hint 2

The longest path from `node` goes through the node itself (1 node) and then continues into the taller of the two subtrees.

## Hint 3

```
if root is None: return 0
return 1 + max(height(root.left), height(root.right))
```
