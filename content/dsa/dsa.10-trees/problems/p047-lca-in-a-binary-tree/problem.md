# Lowest common ancestor in a binary tree

The **lowest common ancestor (LCA)** of two nodes `p` and `q` is the deepest node that has both of them in its subtree. A node counts as a descendant of itself: if `p` is an ancestor of `q`, the LCA is `p`; the LCA of a node with itself is that node.

Write `lca(root, p, q)` for a binary tree that is **not** ordered (not a BST). `p` and `q` are **node objects** that are in the tree, and they may be the same node. Return the LCA **node object**. Values can repeat, so compare nodes with `is`, never by value.

## Example

```python
>>> t = build([3, 5, 1, 6, 2, 0, 8, None, None, 7, 4])
>>> nodes_by_value = {n.val: n for n in nodes(t)}
>>> lca(t, nodes_by_value[5], nodes_by_value[1]).val
3
>>> lca(t, nodes_by_value[5], nodes_by_value[4]).val        # 5 is an ancestor of 4
5
>>> lca(t, nodes_by_value[6], nodes_by_value[4]).val
5
>>> lca(t, nodes_by_value[7], nodes_by_value[7]).val        # a node with itself
7
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2). `nodes(t)` is the tests' helper that lists every node of the tree.

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time, `O(h)` memory.

## Think about

Use the question of chapter section 3: "`lca(node)` returns ___ for the tree that starts at `node`". What does a call return when neither `p` nor `q` is below? When `node` **is** `p` or `q`? What does it mean when **both** children return something?
