# All root-to-leaf paths

Write `root_to_leaf_paths(root)` that returns every path from the root to a leaf as a **string** of the values joined with `"->"`, for example `"1->2->5"`. The paths come in **left-to-right order** of their leaves. An empty tree returns `[]`; a single node returns its own value as a one-item list (`["7"]`). A leaf is a node with no children.

## Example

```python
>>> root_to_leaf_paths(build([1, 2, 3, None, 5]))
['1->2->5', '1->3']
>>> root_to_leaf_paths(build([4, 2, 6, 1, 3, 5, 7]))
['4->2->1', '4->2->3', '4->6->5', '4->6->7']
>>> root_to_leaf_paths(build([-1, -2]))
['-1->-2']
>>> root_to_leaf_paths(None)
[]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n * h)` time (building the strings costs the length of each path).

## Think about

This is the backtracking template of dsa.07 on a tree: **choose** (add the node to the path), **explore** (recurse), **un-choose** (remove it again). When you reach a leaf, a **copy** of the path is stored. Which problem appears if you store the list itself?
