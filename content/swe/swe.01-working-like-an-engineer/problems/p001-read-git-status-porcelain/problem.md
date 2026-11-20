# Read `git status --porcelain`

`git status --porcelain` (or `--short`) prints one line per changed file in a format meant for programs: two status letters `XY`, a space, then the path. `X` is the state in the **index** (staged), `Y` is the state in the **working tree**.

```text
M  a.py        staged modification
 M b.py        unstaged modification (note the leading space)
MM c.py        staged, and modified again after staging
?? d.py        untracked
D  e.py        deleted and the deletion staged
 D f.py        deleted in the working tree, not staged
A  g.py        newly added (staged)
R  old.py -> new.py     renamed (staged)
```

Write `parse_status(text)` that returns a dict with four lists, **in the order the files appear**:

| Key | A file is listed when |
|---|---|
| `"staged"` | `X` is any letter except space and `?` (`M`, `A`, `D`, `R`, `C`) |
| `"modified"` | `Y` is `M` |
| `"deleted"` | `X` is `D` or `Y` is `D` |
| `"untracked"` | the line starts with `??` |

So one file can appear in several lists (`MM c.py` is both staged and modified; `D  e.py` is staged and deleted). For a rename use the **new** path. If a path is wrapped in double quotes (git does this for names with spaces), remove the quotes. Ignore blank lines. Empty text gives four empty lists. All four keys are always present.

## Example

```python
text = "M  a.py\n M b.py\nMM c.py\n?? d.py\nD  e.py\n D f.py\nA  g.py\nR  old.py -> new.py\n"
parse_status(text)
# {"staged": ["a.py", "c.py", "e.py", "g.py", "new.py"],
#  "modified": ["b.py", "c.py"],
#  "deleted": ["e.py", "f.py"],
#  "untracked": ["d.py"]}
```

Tests pass in text only; no git is needed.
