# Diameter

The **diameter** of a tree is the length of the longest path between any two nodes, counted in **edges** (the arrows between nodes; a path of 4 nodes has 3 edges). The path may or may not pass through the root. A single node and the empty tree have diameter `0`.

## Example

```python
>>> diameter(build([3, 9, 20, None, None, 15, 7]))     # 9 - 3 - 20 - 15
3
>>> diameter(build([4, 2, 6, 1, 3, 5, 7]))             # 1 - 2 - 4 - 6 - 7
4
>>> diameter(build([1]))
0
>>> diameter(None)
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

For each node, the longest path that has this node as its **highest point** goes down the deepest left branch and the deepest right branch. Which two numbers do you need from the children? What does the function **return** to its parent, and what does it only **record**?
