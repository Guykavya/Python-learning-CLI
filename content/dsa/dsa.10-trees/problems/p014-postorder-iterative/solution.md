## Approach

Postorder is `L, R, node`. Read it backwards: `node, R, L`, which is an ordinary preorder with the two children swapped. So run the iterative preorder with the roles of left and right exchanged (push the left child first, so the right child is on top and is visited first), collect the values, and reverse the list at the end. Each node is pushed and popped once.

## Code

```python
def postorder_iter(root):
    out = []
    stack = [root] if root is not None else []
    while stack:
        node = stack.pop()
        out.append(node.val)                # node, then right, then left ...
        if node.left is not None:
            stack.append(node.left)
        if node.right is not None:
            stack.append(node.right)
    return out[::-1]                        # ... reversed: left, right, node
```

## Complexity

`O(n)` time. The reversal way keeps the whole visit list before reversing it, so it needs `O(n)` extra memory besides the output; the one-stack way with a `last` pointer needs only `O(h)` extra memory.

## Another way

One stack and a `last` pointer (chapter section 5): go left and push; look at the top; if it has a right child that is not `last`, go into that right child; otherwise visit the top, pop it and set `last` to it:

```python
def postorder_iter(root):
    out, stack, cur, last = [], [], root, None
    while cur is not None or stack:
        while cur is not None:
            stack.append(cur)
            cur = cur.left
        top = stack[-1]
        if top.right is not None and top.right is not last:
            cur = top.right
        else:
            out.append(top.val)
            last = stack.pop()
    return out
```

This keeps the stack at `O(h)` size, but it is harder to get right. The `(node, done)` template of the chapter is a third way.
