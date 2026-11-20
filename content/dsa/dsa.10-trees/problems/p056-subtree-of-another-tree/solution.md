## Approach

A subtree of `root` starts at one of its nodes and contains **all** descendants of that node. So try `same_tree(node, sub)` at every node: at this node, or somewhere in the left subtree, or somewhere in the right subtree. The empty `sub` matches everything (there is nothing to find), and an empty `root` cannot contain a non-empty `sub`.

## Code

```python
def same_tree(a, b):
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    return a.val == b.val and same_tree(a.left, b.left) and same_tree(a.right, b.right)


def is_subtree(root, sub):
    if sub is None:
        return True
    if root is None:
        return False
    return same_tree(root, sub) or is_subtree(root.left, sub) or is_subtree(root.right, sub)
```

## Complexity

`O(n * m)` time in the worst case: `same_tree` may run on up to `n` nodes, each comparing up to `m` nodes. `O(h)` memory for the recursion.

## Another way

Serialise both trees (section 11) and search for the text of `sub` inside the text of `root`: `O(n + m)` with a good string search. It only works if every token has a delimiter **in front of it** (`",2,#,#"` is not found inside `",12,#,#"`), as the chapter shows. The simple `same_tree` at every node is easier to get right.
