# Lowest common ancestor in a BST

In a **binary search tree** the order helps: you do not need to look at both sides. Write `lca_bst(root, p, q)` that returns the lowest common ancestor of the nodes `p` and `q` (node objects that are in the tree; a node is its own ancestor; they may be the same node). The values are distinct.

Use the order: compare the values of `p` and `q` with the current node. The tests count the pointer reads on a BST of 4,095 nodes; the general `lca` of problem 47 looks at both sides and fails the count.

## Example

```python
>>> t = make_bst([20, 10, 30, 5, 15, 25, 40])
>>> n = {x.val: x for x in nodes(t)}
>>> lca_bst(t, n[5], n[15]).val
10
>>> lca_bst(t, n[5], n[10]).val          # 10 is an ancestor of 5
10
>>> lca_bst(t, n[25], n[40]).val
30
>>> lca_bst(t, n[5], n[40]).val
20
```

`make_bst(keys)` is the tests' helper: it inserts the keys one by one into an empty BST. `nodes(t)` lists every node.

## Constraints

- Up to a few thousand nodes. `O(h)` time, `O(1)` extra memory.

## Think about

Three cases at a node: both values smaller, both larger, or anything else. Which case means "the answer is in the left subtree"? Which means "this node is the answer"? Why does it include the case where one of them **equals** the node?
