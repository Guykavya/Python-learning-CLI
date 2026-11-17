## Hint 1

`same_tree(a, b)`: three cases. Both `None`: `True`. Exactly one is `None`: `False`. Both exist: the values must be equal **and** the left subtrees must be the same **and** the right subtrees must be the same. Why can you not compare just the lists of values?

## Hint 2

For `is_symmetric`, write a helper `is_mirror(a, b)` that asks "is `a` the mirror image of `b`?" The base cases are the same as before; for two nodes with equal values, the **left** of `a` must mirror the **right** of `b`, and the **right** of `a` must mirror the **left** of `b`. Then `is_symmetric(root)` compares the two sides of the root.

## Hint 3

```
def same_tree(a, b):
    if a is None and b is None: return True
    if a is None or b is None:  return False
    return a.val == b.val and same_tree(a.left, b.left) and same_tree(a.right, b.right)

def is_mirror(a, b):
    if a is None and b is None: return True
    if a is None or b is None:  return False
    return a.val == b.val and is_mirror(a.left, b.right) and is_mirror(a.right, b.left)

def is_symmetric(root):
    return root is None or is_mirror(root.left, root.right)
```
