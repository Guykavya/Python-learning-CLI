# House robber III (tree)

The houses of a district form a **binary tree**: each node is a house with `node.val` money in it. Two houses that are **directly linked** (a parent and its child) cannot both be robbed. Write `rob_tree(root)` that returns the most money you can rob. `root` is a `TreeNode` (fields `val`, `left`, `right`) or `None` (chapter section 18).

`starter.py` contains the chapter's `TreeNode` class and `build_tree(values)`, which builds a tree from a level-order list (`None` = no child), so you can try examples. The tests build their own trees with the same fields.

## Example

```python
>>> rob_tree(build_tree([3, 2, 3, None, 3, None, 1]))    # rob 3 (root), 3 and 1
7
>>> rob_tree(build_tree([3, 4, 5, 1, 3, None, 1]))       # rob 4 and 5
9
>>> rob_tree(build_tree([2, 1, 3, None, 4]))             # rob 4 and 3
7
>>> rob_tree(None)
0
```

## Constraints

- Up to `2**17 - 1` nodes; the tree height is at most 700. `0 <= node.val <= 10**4`.
- `O(n)` time: every node visited once.

## Think about

When the parent decides, it needs to know two things about each child's subtree: the best total **if the child is robbed** and the best total **if it is not**. What if every call returned both numbers as a pair? Then why is a "rob me and recurse to my grandchildren" recursion slow without a memo?
