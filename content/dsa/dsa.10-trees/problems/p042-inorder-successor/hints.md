## Hint 1

Look at the tree `[20, 10, 30, 5, 15, 25, 40]` and the key `15`. It is a leaf and a right child, so it has no right subtree. Where is the next larger value? Which ancestor is it? Now the key `10`: it has a right subtree. Where is its successor?

## Hint 2

Walk down from the root as in a search for the key. At a node with `key < node.val`, this node is **larger** than the key, so it is a candidate: remember it and go **left** to look for a smaller candidate. Otherwise (`key >= node.val`) the answer is larger than this node, so go **right** and keep the old candidate. When you fall off the tree, the last remembered candidate is the answer.

## Hint 3

```
best = None
cur = root
while cur is not None:
    if key < cur.val:
        best = cur            # a possible answer; try to find a smaller one on the left
        cur = cur.left
    else:
        cur = cur.right       # key >= cur.val: the answer is larger than cur
return best.val if best is not None else None
```
