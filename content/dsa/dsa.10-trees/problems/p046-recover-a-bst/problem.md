# Recover a BST with two swapped values

A binary search tree with distinct values was damaged: the `val` fields of **exactly two nodes** were swapped by mistake. The shape (all `left` and `right` pointers) is unchanged. Write `recover_tree(root)` that repairs the tree **in place** by swapping the two values back. It returns nothing and must not change any `left` or `right` pointer: no node moves.

The two wrong nodes can be neighbours in the sorted order, or far apart (even the root and a leaf).

## Example

```python
>>> t = build([1, 3, None, None, 2])           # 3 and 1 were swapped
>>> recover_tree(t)
>>> to_level(t)
[3, 1, None, None, 2]
>>> t = build([3, 1, 4, None, None, 2])        # 3 and 2 were swapped (neighbours in the sorted order)
>>> recover_tree(t)
>>> to_level(t)
[2, 1, 4, None, None, 3]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2). `to_level` is the opposite helper (the chapter's `to_level_list`).

## Constraints

- Up to a few hundred nodes, depth below the recursion limit. `O(n)` time. `O(h)` extra memory is fine.

## Think about

This idea is not in the chapter, so the hints build it. In a valid BST, the inorder list is **increasing** (section 9). What does the inorder list of the damaged tree look like? Where does it go **down**? How many times can it go down if only two values were swapped?
