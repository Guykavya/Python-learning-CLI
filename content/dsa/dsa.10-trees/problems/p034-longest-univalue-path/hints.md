## Hint 1

Write the sentence: "`down(node)` returns the length (in edges) of the longest path that starts at `node`, goes **down**, and uses only the value `node.val`". What is `down(None)`? When the left child exists and has the same value as `node`, how does the left branch of `node` relate to `down(left child)`?

## Hint 2

For a node: `left_len = down(left) + 1` if the left child has the **same value as this node**, otherwise `0`. The same for the right side. A path that bends at this node has the length `left_len + right_len`: **record** it in `best`. The parent can extend only one branch: **return** `max(left_len, right_len)`.

## Hint 3

```
best = 0
def down(node):
    if node is None: return 0
    left, right = down(node.left), down(node.right)
    left_len  = left + 1  if node.left  and node.left.val  == node.val else 0
    right_len = right + 1 if node.right and node.right.val == node.val else 0
    best = max(best, left_len + right_len)
    return max(left_len, right_len)
```
