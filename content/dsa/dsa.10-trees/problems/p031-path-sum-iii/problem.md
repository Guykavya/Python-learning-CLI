# Path sum III (any downward path)

Write `path_sum_count(root, target)` that returns **how many downward paths** have values that add up to `target`.

A downward path starts at **any** node and goes down through child links (left or right at every step) and may stop at any node below. It does **not** have to start at the root or end at a leaf. A single node is a path. Values can be negative or zero, so a path may reach the target, continue, and reach it again: count every different (start, end) pair.

## Example

```python
>>> path_sum_count(build([10, 5, -3, 3, 2, None, 11, 3, -2, None, 1]), 8)     # 5-3, 5-2-1, -3-11
3
>>> path_sum_count(build([0, 0, 0]), 0)           # three single nodes and two 2-node paths
5
>>> path_sum_count(build([1, -1, 1]), 0)          # only 1 -> -1 (the left side)
1
>>> path_sum_count(None, 0)
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time: the tests count how often you read a `left` or `right` pointer on a perfect tree of 4,095 nodes. Starting a new walk at every node reads `n log n` pointers and fails the count.

## Think about

Chapter section 8: on the way from the root to the current node, let `running` be the sum so far. A path that ends at this node and has the sum `target` starts right after an earlier point whose running sum was `running - target`. What must you keep in a dictionary, and what must you do with it when you leave a node?
