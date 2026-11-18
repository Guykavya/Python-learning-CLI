# Binary tree cameras

You install cameras on the nodes of a binary tree. A camera on a node watches **its parent, itself and its children**. Write `min_cameras(root)` that returns the **fewest** cameras needed so that every node is watched. `root` is a `TreeNode` (fields `val`, `left`, `right`; the values do not matter here) or `None`.

`starter.py` contains the chapter's `TreeNode` and `build_tree(values)` (level order, `None` = no child) for trying examples.

## Example

```python
>>> min_cameras(build_tree([0, 0, None, 0, 0]))        # one camera on the left child
1
>>> min_cameras(build_tree([0, 0, None, 0, None, 0, None, None, 0]))   # a chain of 5 nodes
2
>>> min_cameras(build_tree([0]))
1
>>> min_cameras(None)
0
```

In the second tree (a chain `A - B - C - D - E` going down), cameras on `B` and `D` watch everything.

## Constraints

- Up to `2**17 - 1` nodes; the height is at most 700.
- `O(n)` time.

## Think about

This is not taught as such in the chapter; it is house robber III (section 18) with **three** modes instead of two. For a node, after its whole subtree is handled, the node can be:

1. **not watched yet** (its parent will have to watch it), with everything below it watched;
2. **watched without a camera on it** (a child has one), with everything below watched;
3. **holding a camera**.

What is the fewest cameras in the subtree for each mode, given the three numbers of each child? What should a missing child (`None`) return so that it never forces anything?
