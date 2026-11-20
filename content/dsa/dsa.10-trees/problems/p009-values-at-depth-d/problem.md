# Values at depth d

The **depth** of a node is the number of steps from the root: the root has depth 0, its children depth 1, and so on. Write `values_at_depth(root, d)` that returns the list of the values of all nodes at depth `d`, **from left to right**. If the tree has no node at that depth (`d` is larger than the deepest depth, or the tree is empty), return `[]`.

## Example

```python
>>> t = build([3, 9, 20, None, None, 15, 7])
>>> values_at_depth(t, 0)
[3]
>>> values_at_depth(t, 1)
[9, 20]
>>> values_at_depth(t, 2)
[15, 7]
>>> values_at_depth(t, 5)
[]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- `d >= 0`. Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

This is a **top-down** problem (chapter section 3): the information "how deep am I" travels **down** as a parameter. How can the target depth shrink as you go down, so that the base case is `d == 0`?
