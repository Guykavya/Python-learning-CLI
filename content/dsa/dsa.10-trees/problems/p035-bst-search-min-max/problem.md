# BST search, min, max

In a **binary search tree** every value in the left subtree of a node is smaller than the node, and every value in the right subtree is larger (chapter section 9; the values are distinct). Write three functions:

- `search(root, key)` returns the **node** whose value is `key`, or `None` if there is none.
- `find_min(root)` returns the node with the smallest value, `None` for an empty tree.
- `find_max(root)` returns the node with the largest value, `None` for an empty tree.

Return the node object itself, not its value. Do not change the tree.

## Example

```python
>>> t = build([4, 2, 6, 1, 3, 5, 7])
>>> search(t, 5).val
5
>>> search(t, 8) is None
True
>>> find_min(t).val, find_max(t).val
(1, 7)
>>> find_min(None) is None
True
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- A tree of up to a few thousand nodes. `O(h)` time, where `h` is the height: the tests count pointer reads on a BST of 4,095 nodes, and a search that looks at every node fails the count.

## Think about

At each node one comparison tells you which **whole subtree** can be thrown away. Where is the smallest value of a BST? Where is the largest? Do you need recursion for any of the three?
