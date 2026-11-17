## Hint 1

You know how to ask "are these two trees the same?" (`same_tree`). A subtree is a tree that starts at some node of `root`. So at which nodes of `root` do you ask the question? What do you return if `sub` is empty, and what if `root` is empty but `sub` is not?

## Hint 2

Three parts joined with `or`: the tree that starts at `root` is the same as `sub`, **or** `sub` is a subtree of the left subtree, **or** it is a subtree of the right subtree. Do the empty cases first (`sub is None` gives `True`; `root is None` gives `False`). Write `same_tree` as a helper that compares the whole shape.

## Hint 3

```
def same_tree(a, b):
    if a is None and b is None: return True
    if a is None or b is None:  return False
    return a.val == b.val and same_tree(a.left, b.left) and same_tree(a.right, b.right)

def is_subtree(root, sub):
    if sub is None: return True
    if root is None: return False
    return same_tree(root, sub) or is_subtree(root.left, sub) or is_subtree(root.right, sub)
```
