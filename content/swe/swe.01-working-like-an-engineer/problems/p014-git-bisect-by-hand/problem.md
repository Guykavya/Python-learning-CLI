# `git bisect` by hand

`git bisect` finds the commit that introduced a bug by **binary search** over the history (chapter section 9.7). You tell it one **good** commit (the oldest) and one **bad** commit (the newest); it tests commits in the middle.

Write `first_bad(commits, is_bad)`:

- `commits` is a list, oldest first. `commits[0]` is **known good** and `commits[-1]` is **known bad**; the history has no gaps: once a commit is bad, all later ones are bad.
- `is_bad(commit)` runs the test for one commit and returns `True` when the bug is present. Running it is expensive.
- Return the **first bad commit**.

The tests count how often you call `is_bad`: at most `ceil(log2(n)) + 1` calls for `n` commits, and you must **not** call it on `commits[0]` or `commits[-1]` (you already know their result).

## Example

```python
commits = ["c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7"]
bad_from = {"c5", "c6", "c7"}
first_bad(commits, lambda c: c in bad_from)    # "c5"
```
