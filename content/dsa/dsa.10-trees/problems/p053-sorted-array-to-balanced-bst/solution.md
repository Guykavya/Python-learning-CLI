## Approach

Binary search used to **build** a tree: the middle value is the root, because then the numbers of values on its two sides differ by at most one. Everything before the middle is smaller (it becomes the left subtree) and everything after is larger (the right subtree), so the BST rule holds, and the same rule applies inside each half. With two indices `lo` and `hi` the recursion needs no copy of the list.

## Code

```python
def sorted_to_bst(values):
    def go(lo, hi):                                # the tree of values[lo:hi]
        if lo >= hi:
            return None
        mid = (lo + hi) // 2
        node = TreeNode(values[mid])
        node.left = go(lo, mid)
        node.right = go(mid + 1, hi)
        return node

    return go(0, len(values))
```

## Complexity

`O(n)` time: one call per value and one per empty range. `O(log n)` recursion depth, because each call halves the range.

## Another way

Slicing (`mid = len(values) // 2`, then `sorted_to_bst(values[:mid])` and `values[mid + 1:]`) is shorter but copies the list at each level. If you need a tree from **unsorted** values, sort first, or insert into a balanced tree (the AVL tree of section 14). Choosing the middle to the right (`(lo + hi + 1) // 2`) is just as correct and gives a different shape.
