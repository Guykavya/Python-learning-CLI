## Approach

The stack holds the ancestors that are still waiting for their left subtree to finish. From the current node `cur`, push it and go left until there is no left child. Then pop: that node has nothing left of it that is unvisited, so visit it. Its right subtree comes next, so move `cur` to the right child and repeat. The outer loop runs while there is a node to go down from (`cur`) or a node waiting on the stack.

## Code

```python
def inorder_iter(root):
    out, stack, cur = [], [], root
    while cur is not None or stack:
        while cur is not None:              # go left as far as possible
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()                   # the next node in inorder
        out.append(cur.val)
        cur = cur.right                     # then handle its right subtree
    return out
```

## Complexity

`O(n)` time (each node is pushed once and popped once), `O(h)` stack (the longest left chain of waiting ancestors).

## Another way

Pairs `(node, done)` on the stack (chapter section 5) give inorder, preorder and postorder with one template: push `(right, False)`, `(node, True)`, `(left, False)`. Morris traversal (problem 24) does the same job with no stack at all, by temporarily pointing a right pointer back up.
