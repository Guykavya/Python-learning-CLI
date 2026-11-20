# Maximum value

Write `max_value(root)` that returns the largest value in the tree. For an empty tree return `None`: there is no largest value, and any number you could return (`0`, `-1`, ...) might be a real value of another tree.

## Example

```python
>>> max_value(build([4, 2, 6, 1, 3, 5, 7]))
7
>>> max_value(build([-5, -2, -9]))
-2
>>> max_value(None) is None
True
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Values are integers, possibly negative. Up to a few thousand nodes. `O(n)` time.

## Think about

Which two cases need care: the empty tree, and a child that is empty while the other is not? What would `max(None, 5)` do?
