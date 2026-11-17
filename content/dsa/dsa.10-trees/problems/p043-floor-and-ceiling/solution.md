## Approach

Walk down like a search for `key`. For the floor, a node with a value below `key` is a candidate and a better one (larger, still `<= key`) can only be in its right subtree, so remember it and go right; a node above `key` is too large, so go left; an equal node is the answer. The ceiling is the mirror image. When the walk falls off the tree, the remembered candidate (or `None`) is the answer.

## Code

```python
def floor(root, key):
    best = None
    cur = root
    while cur is not None:
        if key == cur.val:
            return cur.val
        if key > cur.val:
            best = cur                  # <= key: a candidate; a larger one may be on the right
            cur = cur.right
        else:
            cur = cur.left              # too large
    return best.val if best is not None else None


def ceiling(root, key):
    best = None
    cur = root
    while cur is not None:
        if key == cur.val:
            return cur.val
        if key < cur.val:
            best = cur                  # >= key: a candidate; a smaller one may be on the left
            cur = cur.left
        else:
            cur = cur.right             # too small
    return best.val if best is not None else None
```

## Complexity

`O(h)` time for each function, one walk from the root, and `O(1)` extra memory.

## Another way

Keep the sorted inorder list and use `bisect` (dsa.06): `bisect_right(values, key)` gives the floor at `values[i - 1]`, and `bisect_left` gives the ceiling at `values[j]`. That costs `O(n)` to build the list, so it only pays off if the tree does not change and you ask many queries. The tests use exactly this as the brute force.
