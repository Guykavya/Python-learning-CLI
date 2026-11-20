# Right side view

Imagine standing on the **right** side of the tree and looking at it. At each depth you see exactly one node: the rightmost node of that level (which can be a left child if nothing is to its right at that depth). Write `right_side_view(root)` that returns these values from the top level to the bottom level. An empty tree gives `[]`.

## Example

```python
>>> right_side_view(build([1, 2, 3, None, 5, None, 4]))
[1, 3, 4]
>>> right_side_view(build([1, 2, 3, 4]))     # at depth 2 only the left node 4 exists
[1, 3, 4]
>>> right_side_view(build([1, None, 3]))
[1, 3]
>>> right_side_view(None)
[]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes. `O(n)` time.

## Think about

A first idea is "walk down the right children only". Where does that idea fail? Which level information do you really need?
