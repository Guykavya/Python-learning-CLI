## Approach

In an inorder walk, a node `cur` with a left subtree is visited right after the **rightmost node of that left subtree** (its predecessor `pred`). `pred` has no right child, so its `right` pointer can carry a thread back up to `cur`. On the first arrival at `cur`, make the thread and go left. The walk finishes the left subtree and reaches `pred`, whose `right` (the thread) takes it back to `cur`. On the second arrival, the search for `pred` finds `pred.right is cur`: that is the sign that the left subtree is done. Remove the thread (this restores the tree), visit `cur`, and go right. A node without a left child is visited at once and the walk follows its `right` pointer, which may be a thread.

## Code

```python
def morris_inorder(root):
    out, cur = [], root
    while cur is not None:
        if cur.left is None:
            out.append(cur.val)
            cur = cur.right                          # may follow a thread back up
        else:
            pred = cur.left                          # the node visited just before cur
            while pred.right is not None and pred.right is not cur:
                pred = pred.right
            if pred.right is None:
                pred.right = cur                     # make the thread, then go left
                cur = cur.left
            else:
                pred.right = None                    # the left side is done: remove the thread
                out.append(cur.val)
                cur = cur.right
    return out
```

## Complexity

`O(n)` time: every edge on a left subtree's rightmost path is walked at most twice (once when the thread is made, once when it is removed), so the work is at most about `2n` steps in total. `O(1)` extra memory besides the output. The tree is only changed while the walk is running.

## Another way

The iterative stack version (problem 13) is simpler and uses `O(h)` memory; use it unless memory is the issue. Morris is useful when you may not use a stack and may not use recursion (embedded code, huge trees), and it can be changed into a **preorder** (visit when you make the thread) with one line moved. The price: the tree is modified during the walk, so it is not safe when other code reads the tree at the same time.
