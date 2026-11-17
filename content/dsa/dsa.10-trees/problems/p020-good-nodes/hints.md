## Hint 1

A node is good when its value is at least the largest value on the path from the root to it, parent included. So each call needs one extra piece of information from above. Which one? Give the function a second parameter for it.

## Hint 2

Write `go(node, biggest)`, where `biggest` is the maximum of the ancestors. If `node.val >= biggest` the node is good: count 1, and pass `max(biggest, node.val)` down to both children. For the root there are no ancestors: what value of `biggest` makes the root good no matter what its value is?

## Hint 3

```
def go(node, biggest):
    if node is None: return 0
    good = 1 if node.val >= biggest else 0
    biggest = max(biggest, node.val)
    return good + go(node.left, biggest) + go(node.right, biggest)

return go(root, root.val)     # (or float("-inf")); handle the empty tree first
```
