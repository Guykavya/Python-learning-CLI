## Hint 1

Walk down and carry the number spelled by the path so far. At a node with the value `d`, the number becomes `so_far * 10 + d`. The root starts from `0`. When do you add the number to the answer?

## Hint 2

Only at a **leaf**, where the path is complete. For any other node, the answer is the sum of the answers of the two children, both asked with the new number. An empty child contributes `0` (not the number).

## Hint 3

```
def go(node, so_far):
    if node is None: return 0
    so_far = so_far * 10 + node.val
    if node.left is None and node.right is None:
        return so_far
    return go(node.left, so_far) + go(node.right, so_far)

return go(root, 0)
```
