# Flatten a tree to a linked list

Write `flatten(root)` that rearranges the tree **in place** into a "linked list" that uses only the **right** pointers, in **preorder** order (node, left subtree, right subtree). After the call, every node has `left = None`, and following `right` from the root visits all the nodes in the preorder of the **original** tree. Do not create new nodes: the same node objects must be in the same order. `flatten(None)` does nothing. The function returns nothing.

## Example

```python
>>> t = build([1, 2, 5, 3, 4, None, 6])
>>> flatten(t)
>>> chain_values(t)                 # follow .right from the root
[1, 2, 3, 4, 5, 6]
>>> all(node.left is None for node in nodes(t))
True
>>> flatten(None)
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2). `chain_values(t)` follows the `right` pointers and collects the values; `nodes(t)` lists every node.

## Constraints

- Up to a few hundred nodes, depth below the recursion limit. `O(n)` time. The chapter (section 12) shows a loop that needs no recursion and no extra memory.

## Think about

When the current node has a left subtree, where must the node's **old right subtree** go? Which node of the left subtree is the last one in the preorder of that subtree? Why is it the rightmost node?
