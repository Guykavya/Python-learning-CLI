## Hint 1

Take the tree `2` with children `1` and `3`. Start with `cur = 2`. It has a left subtree, so find the node visited just before it: go to `1` and then right as far as possible (nothing). So `pred = 1`. Its `right` is `None`. What single assignment lets the walk, once it has visited `1`, get from `1` back to `2` without a stack?

## Hint 2

`pred.right = cur`: `1.right = 2`. Then go left to `1`. Node `1` has no left child, so visit `1` and move to `1.right`, which is now `2` (the thread). We are at `2` again. Now `pred` is found again, but this time `pred.right is cur`: that is the sign that the left subtree is done. Remove the thread (`pred.right = None`), visit `2`, move to `2.right`.

## Hint 3

```
out, cur = [], root
while cur is not None:
    if cur.left is None:
        out.append(cur.val)
        cur = cur.right                      # may follow a thread
    else:
        pred = cur.left
        while pred.right is not None and pred.right is not cur:
            pred = pred.right
        if pred.right is None:
            pred.right = cur                 # make the thread, go left
            cur = cur.left
        else:
            pred.right = None                # remove the thread: left side is done
            out.append(cur.val)
            cur = cur.right
return out
```
