# Preorder, inorder, postorder (recursive)

Write three functions, each returning the values of the tree as a **list**, in the order of the traversal:

- `preorder(root)`: the node, then the left subtree, then the right subtree,
- `inorder(root)`: the left subtree, then the node, then the right subtree,
- `postorder(root)`: the left subtree, then the right subtree, then the node.

Each returns `[]` for an empty tree. Every call must return a **new** list, and calling a function twice on the same tree must give the same answer twice.

## Example

```python
>>> t = build([4, 2, 6, 1, 3, 5, 7])
>>> preorder(t)
[4, 2, 1, 3, 6, 5, 7]
>>> inorder(t)
[1, 2, 3, 4, 5, 6, 7]
>>> postorder(t)
[1, 3, 2, 5, 7, 6, 4]
>>> preorder(None)
[]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

The three functions differ in only one line. Which one? Can you write a helper `go(node, out)` that appends to a list, and call it from a function that creates the list?
