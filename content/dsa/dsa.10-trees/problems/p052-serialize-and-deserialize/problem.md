# Serialise and deserialise a tree

To save a tree in a file or send it over a network you need a **string** from which the same tree can be rebuilt. Write two functions:

- `serialize(root)` returns a string that describes the tree. An empty tree (`None`) must work too.
- `deserialize(text)` takes **only that string** and returns the root of a tree with the same shape and the same values (new `TreeNode` objects).

The format is yours. The tests do not look at the string: they only check that `deserialize(serialize(tree))` gives back the same tree, for random trees with gaps (nodes with only one child), negative numbers, zero, and numbers with many digits. Chapter section 11 shows a preorder with a marker for each missing child; a level-order list with `None` works too.

## Example

```python
>>> t = build([1, 2, 3, None, None, 4, 5])
>>> s = serialize(t)
>>> isinstance(s, str)
True
>>> to_level(deserialize(s))
[1, 2, 3, None, None, 4, 5]
>>> deserialize(serialize(None)) is None
True
>>> to_level(deserialize(serialize(build([-12, None, 0]))))      # a negative value, a zero, a missing left child
[-12, None, 0]
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2). `to_level` is the opposite helper (the chapter's `to_level_list`).

## Constraints

- Up to a few hundred nodes, depth below the recursion limit. Values are integers (negative, zero and large ones included). `O(n)` time.

## Think about

Why is the plain preorder `1,2,3` not enough? What must you write for a missing child, so that the preorder of the string is unambiguous? Which delimiter keeps `-12` and `1`, `2` apart? Why must `deserialize` read the tokens in the same order in which `serialize` wrote them?
