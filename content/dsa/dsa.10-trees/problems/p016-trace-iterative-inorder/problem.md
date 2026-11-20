# Trace: the iterative inorder

This is the iterative inorder of the chapter (section 5), with a print after every push and every pop. Predict **exactly** what it prints. Do not run it.

```python
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build_tree(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root

def inorder_traced(root):
    out, stack, cur = [], [], root
    while cur or stack:
        while cur:
            stack.append(cur)
            print(f"push {cur.val}: stack={[n.val for n in stack]}")
            cur = cur.left
        cur = stack.pop()
        out.append(cur.val)
        print(f"pop {cur.val}: stack={[n.val for n in stack]} out={out}")
        cur = cur.right
    return out

print(inorder_traced(build_tree([5, 2, 7, 1, 4, 6])))
```

Write your answer in `answer.txt`, one printed line per line. A `push` line shows the stack **after** the push; a `pop` line shows the stack **after** the pop and the list `out` after the visit. The last line is the returned list. The stack is printed from bottom to top, the bottom first.

## How to work

First draw the tree from the list `[5, 2, 7, 1, 4, 6]` (use a queue, as in the previous trace problem). Then keep three things on paper: the current node `cur`, the stack, and `out`. Run the two loops by hand: the inner loop pushes and moves left until `cur` is `None`; then one pop, one visit, and `cur` moves to the right child of the node you popped. Do not skip the times when the right child is `None`: then the next pop takes the node that is next on the stack.

## After you answer

1. At every moment, what do the nodes on the stack have in common?
2. Why does the outer loop test `cur or stack` and not only `stack`?
3. What is the largest size the stack reaches here, and how is that number related to the tree?
