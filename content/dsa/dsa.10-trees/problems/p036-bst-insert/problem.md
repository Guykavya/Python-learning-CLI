# BST insert

Write `insert(root, key)` that puts `key` into the binary search tree and **returns the root** of the tree. The new key goes into a **new leaf**: walk down as in a search until you reach an empty place. If the key is already in the tree, change nothing (the values of a BST are distinct). Inserting into an empty tree (`root` is `None`) returns the new node.

Do not rebuild the tree: the nodes that are already there stay the same objects.

## Example

```python
>>> root = None
>>> for key in (5, 3, 8, 1, 4, 7, 9, 2):
...     root = insert(root, key)
>>> to_level(root)
[5, 3, 8, 1, 4, 7, 9, None, 2]
>>> insert(root, 4) is root              # a duplicate: nothing changes
True
>>> to_level(root)
[5, 3, 8, 1, 4, 7, 9, None, 2]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2). `to_level` is the opposite helper (the chapter's `to_level_list`).

## Constraints

- Up to a few hundred keys, so a recursive version is fine (inserting a sorted sequence of 300 keys makes a chain 300 nodes deep).

## Think about

Why does the function **return** the root, and what goes wrong if you call `insert(root.left, key)` and ignore the result? What does the function return when it reaches `None`?
