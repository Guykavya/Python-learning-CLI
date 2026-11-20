## Approach

The inorder list of a valid BST is increasing. Swapping two values creates one **descent** (a node larger than the next node) if the two values were neighbours in the sorted order, and two descents otherwise. Walk the tree inorder with a `prev` pointer. At the first descent, `prev` is the first wrong node (the value that is too large for its place); at every descent, `cur` is a candidate for the second wrong node, so the last descent wins. Then swap the two `val` fields.

## Code

```python
def recover_tree(root):
    first = second = prev = None
    stack, cur = [], root
    while cur is not None or stack:                # iterative inorder
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        if prev is not None and prev.val > cur.val:    # a descent: the order breaks here
            if first is None:
                first = prev                       # the larger side of the FIRST descent
            second = cur                           # the smaller side of the LATEST descent
        prev = cur
        cur = cur.right
    if first is not None:
        first.val, second.val = second.val, first.val
```

## Complexity

`O(n)` time, a single inorder walk, and `O(h)` memory for the stack. The tree is changed only by the final swap of two values.

## Another way

Collect the nodes in inorder order in a list (`O(n)` memory), take the values, sort them, and write the sorted values back into the nodes in the same order: simple and correct, but `O(n log n)` time and `O(n)` memory. Morris traversal (problem 24) does the same walk with `O(1)` extra memory.
