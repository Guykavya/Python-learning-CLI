# Balanced tree?

A tree is **height-balanced** if for **every** node the heights of its left and right subtrees differ by at most 1 (heights counted in nodes, the empty tree has height 0). Write `is_balanced(root)` that returns `True` or `False`. An empty tree is balanced.

Do it in `O(n)`: the tests count how often your function reads a `left` or `right` pointer on a perfect tree of 4,095 nodes. A solution that calls a separate `height` at every node reads about `n log n` pointers and fails the count.

## Example

```python
>>> is_balanced(build([3, 9, 20, None, None, 15, 7]))
True
>>> is_balanced(build([1, 2, 2, 3, 3, None, None, 4, 4]))
False
>>> is_balanced(build([1, 2, None, 3]))        # a left chain of 3 nodes
False
>>> is_balanced(None)
True
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

The height of a subtree is computed anyway while you walk. Can the same recursive call also report "this subtree is already unbalanced"? (Chapter section 7: return the height, or `-1` as a signal.)
