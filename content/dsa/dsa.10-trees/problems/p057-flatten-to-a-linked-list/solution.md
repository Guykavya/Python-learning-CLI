## Approach

In the preorder, the whole left subtree comes before the right subtree. The last node of the left subtree's preorder is its rightmost node. So for a node with a left subtree: hang the old right subtree on that rightmost node, move the left subtree to the right, and clear `left`. Then continue with `cur.right`. Each node is flattened when the walk reaches it, and nothing is lost, because the old right subtree is always attached before the pointers are changed.

## Code

```python
def flatten(root):
    cur = root
    while cur is not None:
        if cur.left is not None:
            last = cur.left
            while last.right is not None:
                last = last.right              # the rightmost node of the left subtree
            last.right = cur.right             # the old right subtree goes after it
            cur.right = cur.left               # the left subtree moves to the right
            cur.left = None
        cur = cur.right                        # move on along the new right chain
```

## Complexity

`O(n)` time: each node is passed over by the main walk once and by the "rightmost" search at most once. `O(1)` extra memory: no recursion and no stack.

## Another way

A recursive version flattens in **reverse postorder** (right, left, node) and keeps the previously flattened node in a variable `prev`: `node.right = prev; node.left = None; prev = node`. It is short but needs `O(h)` memory for the recursion. Another way is to collect the nodes with an iterative preorder and then link them one after another: `O(n)` memory.
