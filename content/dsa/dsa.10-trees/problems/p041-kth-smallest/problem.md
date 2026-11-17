# K-th smallest in a BST

Write `kth_smallest(root, k)` that returns the **k-th smallest value** in a binary search tree (`k = 1` is the smallest). If the tree has fewer than `k` values, return `None`. The values are distinct. Do not change the tree.

The inorder traversal of a BST is sorted (chapter section 9), so the answer is the k-th node of an inorder walk. **Stop as soon as you have it**: the tests count the pointer reads on a BST of 4,095 nodes, and a function that builds the whole inorder list first fails the count.

## Example

```python
>>> t = build([5, 3, 6, 2, 4, None, None, 1])
>>> [kth_smallest(t, k) for k in range(1, 7)]
[1, 2, 3, 4, 5, 6]
>>> kth_smallest(t, 7) is None
True
>>> kth_smallest(None, 1) is None
True
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(h + k)` time.

## Think about

The iterative inorder of chapter section 5 gives the values one at a time. Where in that loop do you count? What lets you return early?
