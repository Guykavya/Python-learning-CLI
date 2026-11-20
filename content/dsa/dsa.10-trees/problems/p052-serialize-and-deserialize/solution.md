## Approach

A preorder with a marker `#` for every missing child describes a tree without ambiguity, because after each node come exactly its left subtree and its right subtree, each either a marker or a node followed by its own two subtrees. `serialize` is the recursive preorder that appends one token per call and joins them with commas. `deserialize` reads the tokens with an iterator in the same order: a marker means `None`; otherwise it makes a node and builds the left subtree and then the right subtree from the next tokens.

## Code

```python
def serialize(root):
    out = []

    def go(node):
        if node is None:
            out.append("#")                    # a marker for a missing child
            return
        out.append(str(node.val))
        go(node.left)
        go(node.right)

    go(root)
    return ",".join(out)


def deserialize(text):
    tokens = iter(text.split(","))

    def go():
        token = next(tokens)
        if token == "#":
            return None
        node = TreeNode(int(token))
        node.left = go()
        node.right = go()
        return node

    return go()
```

## Complexity

`O(n)` time and `O(n)` space for the string (`2n + 1` tokens for `n` nodes), `O(h)` for the recursion.

## Another way

Use the **level-order list** with `None` for the gaps (the format of `build` and `to_level`), turned into a string with `",".join(...)`. It is the format used by many websites. Deserialising needs a queue, so it works without recursion, which is better for very deep trees. Another format: JSON (`json.dumps` of nested lists or dictionaries).
