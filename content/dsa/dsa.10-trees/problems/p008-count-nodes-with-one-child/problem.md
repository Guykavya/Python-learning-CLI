# Count nodes with one child

Write `count_one_child(root)` that returns how many nodes have **exactly one** child (a left child or a right child, but not both and not none).

## Example

```python
>>> count_one_child(build([1, 2, None, 3]))        # 1 and 2 each have one child
2
>>> count_one_child(build([1, 2, 3]))              # one node has two children, the others none
0
>>> count_one_child(build([1, None, 2]))
1
>>> count_one_child(None)
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes. `O(n)` time.

## Think about

How do you test "exactly one of the two children exists" without writing four `if` branches? (`(a is None) != (b is None)` is true exactly when one of them is `None` and the other is not.)
