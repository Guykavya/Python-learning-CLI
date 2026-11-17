# Size of a tree

Write `size(root)` that returns the number of nodes in the tree that starts at `root`. An empty tree (`root` is `None`) has size 0.

Use the question of chapter section 3: "`size(node)` returns ___ for the tree that starts at `node`." Then answer the two small questions: what does `size(None)` return, and how do you get `size(node)` from `size(node.left)` and `size(node.right)`?

## Example

```python
>>> size(build([4, 2, 6, 1, 3, 5, 7]))
7
>>> size(build([1, None, 2]))
2
>>> size(None)
0
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, balanced or not (the tests stay below the recursion limit). `O(n)` time.

## Think about

How many calls does your function make for a tree with `n` nodes? (Chapter section 3 says exactly `2n + 1`.) Why must `size(None)` be `0` and not `1`?
