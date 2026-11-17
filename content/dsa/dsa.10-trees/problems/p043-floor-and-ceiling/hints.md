## Hint 1

Walk down from the root as in a search. For the **floor**, a node with value `<= key` could be the answer (it is not too large), but a larger candidate may be hiding in its right subtree. What do you remember, and which way do you go?

## Hint 2

Floor: if `node.val == key` return it at once. If `node.val < key`, remember it as the best so far and go **right**. If `node.val > key`, go **left** (the node is too large). Ceiling is the mirror image: a node with `val > key` is remembered and you go left; with `val < key` you go right.

## Hint 3

```
floor(root, key):
    best = None; cur = root
    while cur is not None:
        if cur.val == key: return cur.val
        if cur.val < key: best = cur; cur = cur.right
        else:             cur = cur.left
    return best.val if best is not None else None
```
