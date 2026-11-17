# Mirror (invert) a tree

Write `invert(root)` that turns the tree into its mirror image: at **every** node the left and the right subtree swap places. Do it **in place**: do not create new nodes, only rewire the `left` and `right` pointers of the nodes you have. Return the root of the inverted tree (the same node object you got). `invert(None)` returns `None`.

## Example

```python
>>> t = build([4, 2, 6, 1, 3, 5, 7])
>>> to_level(invert(t))
[4, 6, 2, 7, 5, 3, 1]
>>> to_level(invert(build([1, 2, None, 3])))      # a left chain becomes a right chain
[1, None, 2, None, 3]
>>> invert(None) is None
True
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2). `to_level` is the opposite helper (the chapter's `to_level_list`).

## Constraints

- Up to a few thousand nodes. `O(n)` time.

## Think about

After the swap, which node does `root.left` point to? If you assign `root.left = invert(root.right)` first and then `root.right = invert(root.left)`, what does the second line see?
