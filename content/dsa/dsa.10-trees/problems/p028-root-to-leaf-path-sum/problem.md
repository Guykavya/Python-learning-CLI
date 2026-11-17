# Has a root-to-leaf path with sum

Write `has_path_sum(root, target)` that returns `True` if there is a path from the **root** down to a **leaf** whose values add up to `target`, and `False` otherwise. A leaf is a node with no children. Values can be negative. An empty tree has no path, so the answer is `False` for every `target`, also `0`.

## Example

```python
>>> t = build([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1])
>>> has_path_sum(t, 22)            # 5 -> 4 -> 11 -> 2
True
>>> has_path_sum(t, 5)             # the root alone is not a leaf
False
>>> has_path_sum(build([1, 2]), 1)
False
>>> has_path_sum(None, 0)
False
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

Pass the **remaining** sum down: `target - node.val`. At which kind of node do you compare the remaining sum with the node's value? Why is "the remaining sum is 0 at a `None`" a wrong test?
