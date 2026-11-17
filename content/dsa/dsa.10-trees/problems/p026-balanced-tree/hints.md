## Hint 1

The obvious solution calls `height` for both children at every node. How many times is the same node visited by all these calls? Instead, can one function return **two things in one number**: "how tall is this subtree" and "is it balanced"?

## Hint 2

Let `check(node)` return the height of the subtree, or `-1` when the subtree is not balanced. An empty tree returns `0`. If either child returns `-1`, return `-1` at once (do not look at the other side's height). If the two heights differ by more than 1, return `-1`. Otherwise return `1 + max(left, right)`.

## Hint 3

```
def check(node):
    if node is None: return 0
    left = check(node.left)
    if left == -1: return -1
    right = check(node.right)
    if right == -1 or abs(left - right) > 1: return -1
    return 1 + max(left, right)

return check(root) != -1
```
