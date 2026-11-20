## Hint 1

Finish the sentence: "`max_value(node)` returns the largest value in the tree that starts at `node`, or `None` if there is no node". The two subtrees can each be empty. How do you combine "a number or `None`" from the left with "a number or `None`" from the right and the node's own value?

## Hint 2

Start with `best = node.val`. For each of the two answers that is not `None`, keep the larger one. An answer of `None` means "that side has nothing", so it is simply ignored.

## Hint 3

```
if root is None: return None
best = root.val
for child in (root.left, root.right):
    sub = max_value(child)
    if sub is not None and sub > best:
        best = sub
return best
```
