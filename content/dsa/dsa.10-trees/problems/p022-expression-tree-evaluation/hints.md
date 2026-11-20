## Hint 1

Finish the sentence: "`evaluate(node)` returns the value of the expression that starts at `node`". For a leaf the value is the number itself. For an operator node, what do you need before you can compute anything?

## Hint 2

You need the values of both children: that is **postorder** (children first). Then look at the operator string and apply it to the two values, left value first. A leaf is a node with no left and no right child.

## Hint 3

```
if root.left is None and root.right is None: return root.val
a = evaluate(root.left)
b = evaluate(root.right)
if root.val == "+": return a + b
if root.val == "-": return a - b
if root.val == "*": return a * b
return a / b
```
