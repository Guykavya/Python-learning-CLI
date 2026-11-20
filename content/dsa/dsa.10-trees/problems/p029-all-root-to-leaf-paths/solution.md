## Approach

Keep one shared list `path` with the values from the root to the current node. Entering a node adds its value (choose); leaving it removes the value (un-choose), so that the next branch sees the right path. At a leaf the path is complete: join it into a string and store the string. The tree is the search tree of the backtracking: the two choices at every step are "go left" and "go right".

## Code

```python
def root_to_leaf_paths(root):
    result, path = [], []

    def go(node):
        if node is None:
            return
        path.append(node.val)                                  # choose
        if node.left is None and node.right is None:
            result.append("->".join(map(str, path)))          # a string is a new object: no copy needed
        else:
            go(node.left)
            go(node.right)
        path.pop()                                             # un-choose

    go(root)
    return result
```

## Complexity

`O(n * h)` time in the worst case, because each stored path costs its length to build (a tree of height `h` has at most `n` paths, each of length at most `h`). `O(h)` extra memory for `path` and the stack, plus the output.

## Another way

Pass the text down instead of sharing a list: `go(node, text)` with `text + "->" + str(node.val)`. Strings are new objects at each step, so there is nothing to un-choose; it is simpler, and a little slower for long paths. For a list of lists as output (`[[1, 2, 5], [1, 3]]`), store `path[:]` (a **copy**) at the leaf, as in the chapter (section 8).
