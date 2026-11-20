## Approach

```python
def plan_tree(rows):
    children = {}
    for node_id, parent, _unused, detail in rows:
        children.setdefault(parent, []).append((node_id, detail))
    lines = []
    stack = [(node, 0) for node in sorted(children.get(0, []), reverse=True)]
    while stack:
        (node_id, detail), depth = stack.pop()
        lines.append("  " * depth + detail)
        for child in sorted(children.get(node_id, []), reverse=True):
            stack.append((child, depth + 1))
    return "\n".join(lines)
```

The flat list becomes a dictionary `parent -> children`. The stack holds `(node, depth)` pairs; popping gives the next line to print, and the children go on the stack in **reverse** order so that the first child comes out first. Sorting the children tuples sorts by `id` (the first element).

Example: roots are ids 2 and 7. The stack starts as `[7, 2]` (reversed), so 2 is popped first, printed at depth 0; its child 9 is pushed and printed next at depth 1, then 12 at depth 2; then 7.

## Complexity

`O(n log n)` for the sorting, no recursion.

## Another way

A recursive generator is shorter, but a very deep plan hits the recursion limit. Real plans are shallow; the habit of an explicit stack is what counts.

## Why it matters

Reading a plan as an indented tree shows which step is inside which: a `SCAN` inside a sub-query is a different problem from a `SCAN` at the top.
