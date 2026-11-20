# Distance between two nodes

Write `distance(root, p, q)` that returns the number of **edges** on the path between the nodes `p` and `q` of a binary tree (not necessarily a BST). `p` and `q` are node objects that are in the tree, and they may be the same node (distance 0). Compare nodes with `is`, not by value: values can repeat.

## Example

```python
>>> t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
>>> n = {x.val: x for x in nodes(t)}
>>> distance(t, n[7], n[8])        # 7 - 2 - 5 - 3 - 1 - 8
5
>>> distance(t, n[6], n[4])        # 6 - 5 - 2 - 4
3
>>> distance(t, n[5], n[7])        # 5 is an ancestor of 7: 5 - 2 - 7
2
>>> distance(t, n[5], n[5])
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2). `nodes(t)` is the tests' helper that lists every node of the tree.

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

Chapter section 10: once you know the lowest common ancestor, the path from `p` up to it and from it down to `q` are two straight paths. If `depth` counts the edges from the root, which formula gives the distance from `depth(p)`, `depth(q)` and `depth(LCA)`?
