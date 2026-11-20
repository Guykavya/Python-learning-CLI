## Hint 1

Write the search recursively, with the current node and the position `i` in the pattern. A normal letter follows one edge (or fails). A `.` tries **every** child, and succeeds if any of them succeeds.

## Hint 2

At the end of the pattern (`i == len(pattern)`) the answer is `node.is_end`: the stored word must end exactly here. That is what makes `b.` false.

## Hint 3

```
def match(node, i):
    if i == len(pattern): return node.is_end
    ch = pattern[i]
    if ch == ".":
        return any(match(child, i + 1) for child in node.children.values())
    child = node.children.get(ch)
    return child is not None and match(child, i + 1)
```

`any(...)` with a generator stops at the first `True`.
