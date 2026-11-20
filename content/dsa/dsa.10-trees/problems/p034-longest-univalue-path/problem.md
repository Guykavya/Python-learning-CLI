# Longest univalue path

A **univalue path** is a path (it may go up and then down, with one highest node) in which **every node has the same value**. Write `longest_univalue_path(root)` that returns the length of the longest such path in **edges**. A single node has length 0, and so has the empty tree.

## Example

```python
>>> longest_univalue_path(build([5, 4, 5, 1, 1, None, 5]))      # 5 - 5 - 5 along the right side
2
>>> longest_univalue_path(build([1, 4, 5, 4, 4, None, 5]))      # 4 - 4 - 4 below the left child
2
>>> longest_univalue_path(build([2, 2, 2]))                     # 2 - 2 - 2 bends at the root
2
>>> longest_univalue_path(build([1, 2, None, 1]))               # 1 - 2 - 1 is not a univalue path
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

This is the third style of the paths section: return one branch, record the bent path. At a node, a branch continues into a child only if the child has the **same value as this node**. What does the function return to the parent, and what does it only record?
