## Approach

The value of an operator node needs the values of both operands, so the children come first: this is postorder. A leaf (no children) is a number and returns itself. Otherwise evaluate the left child, evaluate the right child, and combine them with the operator in the node, keeping the order `left op right`.

## Code

```python
def evaluate(root):
    if root.left is None and root.right is None:       # a leaf: a number
        return root.val
    a = evaluate(root.left)                            # postorder: both children first
    b = evaluate(root.right)
    if root.val == "+":
        return a + b
    if root.val == "-":
        return a - b
    if root.val == "*":
        return a * b
    return a / b
```

## Complexity

`O(n)` time, each node is evaluated once. `O(h)` stack.

## Another way

A table of operators (`ops = {"+": operator.add, ...}`, or the lambdas of the chapter) replaces the `if` chain. Or convert the tree to postfix with a postorder walk (`3 4 + 2 *`) and use the stack evaluator of dsa.08: that is the same computation, with an explicit stack instead of recursion.
