## Hint 1

Stand at the root of the tree. If both `p.val` and `q.val` are smaller than the root's value, where are both nodes? Which subtree do you move to? If one is smaller and one is larger, can the LCA be below this node?

## Hint 2

Walk down with a loop. Both values smaller: go left. Both larger: go right. Otherwise (they are split, or one of them equals the node) the current node is the LCA: return it. You never need the whole tree.

## Hint 3

```
cur = root
while cur is not None:
    if p.val < cur.val and q.val < cur.val:   cur = cur.left
    elif p.val > cur.val and q.val > cur.val: cur = cur.right
    else:                                      return cur
return None
```
