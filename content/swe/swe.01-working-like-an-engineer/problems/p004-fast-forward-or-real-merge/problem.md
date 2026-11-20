# Fast-forward or real merge?

You are on branch `current` and run `git merge other`. What will git do (chapter sections 5.4 and 5.5)?

- `"up-to-date"`: `other` is already part of your history (it is an ancestor of `current`, or the same commit). Git says "Already up to date" and changes nothing.
- `"fast-forward"`: your branch is an ancestor of `other`; git only moves your branch pointer forward. No new commit.
- `"merge"`: both lines have moved on; git creates a **merge commit** with two parents.

Write `merge_kind(graph, current, other)`. The graph is a dict `{sha: [parents]}` as in the previous problem; `current` and `other` are commit hashes. A commit counts as an ancestor of itself.

## Example

```text
graph:   a <- b <- c          branches: current = c
              \
               d <- e         other   = e
```

```python
graph = {"a": [], "b": ["a"], "c": ["b"], "d": ["b"], "e": ["d"]}
merge_kind(graph, "c", "e")   # "merge": c and e have diverged at b
merge_kind(graph, "d", "e")   # "fast-forward": d is an ancestor of e
merge_kind(graph, "e", "d")   # "up-to-date": d is already in e's history
merge_kind(graph, "c", "c")   # "up-to-date"
```
