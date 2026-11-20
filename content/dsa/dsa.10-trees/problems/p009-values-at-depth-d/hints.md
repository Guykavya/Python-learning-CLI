## Hint 1

Finish the sentence: "`values_at_depth(node, d)` returns the values `d` levels below `node`". For `d = 0`, which node is it? For `d = 1`, which nodes are those, in terms of `node.left` and `node.right`?

## Hint 2

The nodes `d` levels below `node` are the nodes `d - 1` levels below its left child, followed by those below its right child. Left first, so the order is left to right. The base cases: `None` gives `[]`, and `d == 0` gives `[node.val]`.

## Hint 3

```
if root is None: return []
if d == 0: return [root.val]
return values_at_depth(root.left, d - 1) + values_at_depth(root.right, d - 1)
```
