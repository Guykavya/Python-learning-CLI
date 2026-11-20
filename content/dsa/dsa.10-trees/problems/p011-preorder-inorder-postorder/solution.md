## Approach

All three have the same skeleton: the answer for a tree is the lists of the two subtrees and the node's own value `[node.val]`, joined in some order. The only difference is where `[node.val]` goes: first (preorder), between (inorder) or last (postorder). The empty tree returns `[]`.

## Code

```python
def preorder(root):
    if root is None:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)


def inorder(root):
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


def postorder(root):
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]
```

## Complexity

`O(n)` calls. Joining lists copies values, so the version above costs `O(n * h)` in the worst case (a chain copies a growing list at each level), `O(n log n)` for a balanced tree. The helper version below is `O(n)`. Stack depth `O(h)`.

## Another way

The version that creates one list and fills it is `O(n)` in total and is the one used in the chapter (section 4):

```python
def inorder(root):
    out = []

    def go(node):
        if node is None:
            return
        go(node.left)
        out.append(node.val)
        go(node.right)

    go(root)
    return out
```

The list is created **inside** `inorder`, so every call starts with an empty one. The helper `go` can see it because it is defined inside the function.
