## Hint 1

Pick any node `v`. Look at the longest path whose highest node is `v`: it goes down on the left as far as possible, and down on the right as far as possible. Its length in edges is `height(left) + height(right)`, with heights counted in nodes. What do you have to compute for every node to get this number?

## Hint 2

Write `go(node)` that returns the height of `node`'s subtree (the parent needs it). While computing it, at each node compute `left + right` and keep the largest such number in a variable shared by all the calls (`nonlocal best`). The answer is `best` after the whole walk. The function returns one thing for its parent and records another for the answer.

## Hint 3

```
best = 0
def go(node):
    nonlocal best
    if node is None: return 0
    left, right = go(node.left), go(node.right)
    best = max(best, left + right)
    return 1 + max(left, right)
go(root)
return best
```
