## Approach

Because of the BST rule, one comparison at each node rules out a whole subtree: a smaller key can only be on the left, a larger one only on the right. So `search` is a loop that moves one step down per comparison and returns `None` when it falls off the tree. The smallest value has nothing smaller to its left, so it is the leftmost node; the largest is the rightmost.

## Code

```python
def search(root, key):
    cur = root
    while cur is not None:
        if key == cur.val:
            return cur
        cur = cur.left if key < cur.val else cur.right
    return None


def find_min(root):
    if root is None:
        return None
    while root.left is not None:
        root = root.left              # the smallest value is the leftmost node
    return root


def find_max(root):
    if root is None:
        return None
    while root.right is not None:
        root = root.right
    return root
```

## Complexity

`O(h)` time for all three: one step down per level, and `O(1)` extra memory (no recursion, no stack). For a balanced tree `h` is about `log n`; for a chain it is `n`.

## Another way

`search` can be written recursively (`return search(root.left, key) if key < root.val else ...`), which costs `O(h)` stack. Searching with a loop is the same walk without that cost, and it is what a balanced tree's `contains` uses in real libraries.
