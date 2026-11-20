# Traversal generator

Write `iter_inorder(root)`, a **generator**: it hands out the values of the tree in inorder **one at a time**, doing only the work that is needed for the next value. For an empty tree it yields nothing.

```python
>>> t = build([4, 2, 6, 1, 3, 5, 7])
>>> g = iter_inorder(t)
>>> next(g), next(g), next(g)
(1, 2, 3)
>>> list(iter_inorder(t))
[1, 2, 3, 4, 5, 6, 7]
>>> list(iter_inorder(None))
[]
```

The tests take only the first 3 values from a search tree with 32,767 nodes and count how many times your function reads a `left` or `right` pointer. If your function first builds the whole list and then yields from it, it reads every pointer, and the test fails: the point of a generator is **laziness**.

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- The tests keep the height below 100, so an explicit stack and `yield from` recursion both work. Taking `k` values from a balanced tree must cost about `O(h + k)`, not `O(n)`.

## Think about

Where does a generator pause? What must you remember between two `next()` calls, and where do you keep it? (The explicit stack of problem 13 is exactly that memory.)
