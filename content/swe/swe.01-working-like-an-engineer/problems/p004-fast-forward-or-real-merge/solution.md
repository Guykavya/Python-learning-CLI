## Approach

```python
def ancestors(graph, sha):
    seen = {sha}
    stack = [sha]
    while stack:
        c = stack.pop()
        for p in graph.get(c, []):
            if p not in seen:
                seen.add(p)
                stack.append(p)
    return seen


def merge_kind(graph, current, other):
    if other in ancestors(graph, current):
        return "up-to-date"
    if current in ancestors(graph, other):
        return "fast-forward"
    return "merge"
```

The order of the two questions matters. When `current == other`, both are true; the first check makes it `up-to-date`, which is what git says. A fast-forward is only possible when there is nothing in `current` that `other` lacks.

Example: `merge_kind(graph, "c", "e")`: ancestors of `c` are `{c, b, a}`; `e` is not among them. Ancestors of `e` are `{e, d, b, a}`; `c` is not among them. So the lines diverged: `merge`.

## Complexity

`O(commits)` per call.

## Another way

Git itself asks `git merge-base --is-ancestor A B`, which exits with 0 when `A` is an ancestor of `B`. That is the same test.

## Why it matters

You can predict whether `git merge` will create a merge commit before you run it. `--no-ff` forces the `merge` outcome even where a fast-forward would be possible (chapter section 5.6).
