# Sum of all values

Write `tree_sum(root)` that returns the sum of all values in the tree. The values are integers and **may be negative**. The sum of an empty tree is 0.

## Example

```python
>>> tree_sum(build([1, 2, 3]))
6
>>> tree_sum(build([5, -8, 2]))
-1
>>> tree_sum(None)
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes. `O(n)` time.

## Think about

Which line of your function would break if all values were negative? (A function that starts with `best = 0` for a sum would be wrong in the next problem.)
