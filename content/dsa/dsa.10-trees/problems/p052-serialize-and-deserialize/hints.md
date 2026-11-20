## Hint 1

The preorder `[1, 2]` belongs to two different trees (`2` as left child or as right child). A marker for a missing child fixes this: every node is followed by **exactly** its left subtree and its right subtree, and a missing subtree is a marker such as `#`. How many tokens does a tree with `n` nodes have, with the markers?

## Hint 2

`serialize`: a recursive preorder that appends `str(node.val)` for a node and `"#"` for `None`, then `",".join(tokens)`. `deserialize`: split the string on the commas and take the tokens one by one with an iterator. A helper `go()` takes the next token: if it is `#` return `None`; otherwise make a node, build its left subtree with `go()` and then its right subtree with `go()`.

## Hint 3

```
serialize(root):
    out = []
    def go(node):
        if node is None: out.append("#"); return
        out.append(str(node.val)); go(node.left); go(node.right)
    go(root); return ",".join(out)

deserialize(text):
    tokens = iter(text.split(","))
    def go():
        token = next(tokens)
        if token == "#": return None
        node = TreeNode(int(token))
        node.left = go(); node.right = go()
        return node
    return go()
```
