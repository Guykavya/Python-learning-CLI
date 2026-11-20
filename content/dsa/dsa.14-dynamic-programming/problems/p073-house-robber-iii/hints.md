## Hint 1

Let `go(node)` return a pair `(rob, skip)`: the best total in the subtree of `node` when `node` **is** robbed, and when it is **not**. A missing child returns `(0, 0)`. The answer is `max(go(root))`.

## Hint 2

- If `node` is robbed, its children must not be: `rob = node.val + lskip + rskip`.
- If `node` is not robbed, each child is free to be robbed or not, whichever is better: `skip = max(lrob, lskip) + max(rrob, rskip)`.

The second line is the one most people get wrong: "skip the node" does **not** mean "rob the children".

## Hint 3

```
def go(node):
    if node is None: return (0, 0)
    lrob, lskip = go(node.left)
    rrob, rskip = go(node.right)
    return (node.val + lskip + rskip, max(lrob, lskip) + max(rrob, rskip))
return max(go(root))
```
