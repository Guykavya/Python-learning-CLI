# Range sum in a BST

Write `range_sum(root, lo, hi)` that returns the sum of all values `v` in the binary search tree with `lo <= v <= hi` (both ends included). It is `0` if no value is in the range or the tree is empty. The values are distinct integers. `lo <= hi`.

The BST order lets you **skip** parts of the tree (**pruning**, as in the backtracking module). The tests count the pointer reads on a BST of 4,095 nodes for a range of 11 values: a function that visits every node reads about 8,000 pointers and fails; about 70 are enough.

## Example

```python
>>> t = make_bst([10, 5, 15, 3, 7, 18])
>>> range_sum(t, 7, 15)               # 7 + 10 + 15
32
>>> range_sum(t, 6, 10)               # 7 + 10
17
>>> range_sum(t, 20, 30)
0
>>> range_sum(None, 0, 5)
0
```

`make_bst(keys)` is the tests' helper: it inserts the keys one by one into an empty BST.

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(h + m)` time, where `m` is the number of values inside the range.

## Think about

At a node with value `v` below `lo`, which subtree can you skip? At a value above `hi`? What do you do at a node that is inside the range?
