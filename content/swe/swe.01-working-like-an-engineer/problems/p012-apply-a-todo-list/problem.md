# Apply a todo list (with `--autosquash`)

Model two parts of `git rebase -i` on plain data.

Commits are pairs `(sha, subject)`, oldest first.

## Part 1: `apply_todo(commits, todo)`

`todo` is a list of steps, run from top to bottom. A step is a tuple:

- `("pick", sha)`: keep the commit with its subject;
- `("reword", sha, new_subject)`: keep the commit, with `new_subject`;
- `("squash", sha)` or `("fixup", sha)`: meld the commit into the commit **just before it in the result**; the subject of that commit stays;
- `("drop", sha)`: remove the commit.

Return the list of **subjects** of the resulting history, oldest first. Commits that do not appear in the todo list are lost (git: "if you remove a line, that commit will be lost"). `squash` or `fixup` with no earlier commit in the result (for example as the first step, or only after drops) raises `ValueError`, like git. An unknown command or sha raises `ValueError`.

## Part 2: `autosquash(commits)`

Build the todo list that `git rebase -i --autosquash` would offer. Each commit gives a step. A commit whose subject starts with `fixup! ` or `squash! ` is moved **right after** the commit whose subject is the rest of the text (the earliest such commit before it) and gets the command `fixup` or `squash`; the other commits are `pick`. A `fixup!` with no target before it stays where it is, as a `pick`. Several fixups for the same target keep their relative order.

Return a list of `(command, sha)` tuples.

## Example

```python
commits = [("a1", "Add login"), ("b2", "Add search"), ("c3", "fixup! Add login"), ("d4", "Add docs")]
autosquash(commits)
# [("pick", "a1"), ("fixup", "c3"), ("pick", "b2"), ("pick", "d4")]

apply_todo(commits, [("pick", "a1"), ("fixup", "c3"), ("pick", "b2"), ("drop", "d4")])
# ["Add login", "Add search"]
```
