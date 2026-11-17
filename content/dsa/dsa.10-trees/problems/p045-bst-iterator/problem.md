# BST iterator

Write a class `BSTIterator` that walks a binary search tree **one value at a time, in increasing order**:

- `BSTIterator(root)` prepares the walk (the tree may be empty).
- `next()` returns the next smallest value and moves on. When there is no next value it raises `StopIteration`.
- `has_next()` returns `True` if `next()` would return a value, otherwise `False`.

The memory must be `O(h)` (the height), not `O(n)`: do **not** copy the whole tree into a list in the constructor. The tests count the pointer reads: creating the iterator on a tree of 4,095 nodes and taking three values must read only a few dozen pointers.

## Example

```python
>>> it = BSTIterator(build([7, 3, 15, None, None, 9, 20]))
>>> [it.next(), it.next(), it.has_next()]
[3, 7, True]
>>> [it.next(), it.next(), it.next(), it.has_next()]
[9, 15, 20, False]
>>> BSTIterator(None).has_next()
False
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes. `next()` and `has_next()` are `O(1)` on average (amortised) and use `O(h)` memory. Two iterators on the same tree must not disturb each other.

## Think about

The iterative inorder of section 5 keeps a stack. What if the stack is the **state** of the iterator, and each `next()` runs only one step of the loop? Which nodes are on the stack right after the constructor?
