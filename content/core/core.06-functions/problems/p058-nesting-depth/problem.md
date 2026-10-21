# How deep is the nesting?

Write `depth(data)` that returns how deeply lists and tuples are nested in `data`:

- anything that is not a list or tuple has depth `0`;
- a list or tuple has depth `1 +` the largest depth of its items; an **empty** list or tuple has
  depth `1`.

Strings are not containers here (a string has depth 0).

**Examples**

```python
depth(5)                    # 0
depth("abc")                # 0
depth([])                   # 1
depth([1, 2, 3])            # 1
depth([1, [2, [3]], 4])     # 3
depth([[], [[]]])           # 3
depth((1, [2, (3, [])]))    # 4
```
