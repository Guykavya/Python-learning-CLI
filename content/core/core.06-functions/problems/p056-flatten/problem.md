# Flatten nested lists

Write `flatten(nested)` that returns a **new flat list** of all the non-list items in `nested`,
in order, however deeply the lists are nested. Only **lists** count as nesting; strings, tuples
and numbers are items. The input must not change.

**Examples**

```python
flatten([1, [2, [3, 4]], 5, [[6]], []])   # [1, 2, 3, 4, 5, 6]
flatten([])                               # []
flatten([[[]]])                           # []
flatten(["ab", ["cd", ("e", "f")]])       # ['ab', 'cd', ('e', 'f')]
```

`isinstance(item, list)` tells you whether an item is a list.
